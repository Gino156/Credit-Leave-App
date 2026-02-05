from datetime import datetime, timedelta, timezone, date
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Local imports
import jwt
from pwdlib import PasswordHash
import models
from database import get_auth_db, get_payroll_db, pg_engine, BaseAuth

# --- 0. AUTO-CREATE POSTGRES TABLE ---
BaseAuth.metadata.create_all(bind=pg_engine)

app = FastAPI(title="Leave Credit App")

# --- 1. MIDDLEWARE SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SECURITY CONFIG ---
SECRET_KEY ="f34fb792147d3f5b418cebec18fd2b192b961b2acae5cdb1136f9dc5acc7ae52"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- HELPERS ---
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def get_user(db: Session, username: str):
    return db.query(models.UserTable).filter(models.UserTable.username == username).first()

# --- DEPENDENCIES ---
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_auth_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None: raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
        
    user = get_user(db, username=username)
    if user is None: raise credentials_exception
    return user

# --- ROUTES ---

@app.get("/")
async def root():
    return {"message": "Leave Credit App API is running"}

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_auth_db)
) -> models.Token:
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return models.Token(access_token=access_token, token_type="bearer")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.get("/LeaveHistory")
async def get_leave_history(
    current_user: Annotated[models.UserTable, Depends(get_current_user)],
    db: Session = Depends(get_payroll_db)
):
    # Naka-sort DESC para ang index [0] sa frontend ay ang pinaka-latest
    return db.query(models.vw_TimeOffSummary).filter(
        models.vw_TimeOffSummary.EmployeeID == current_user.id
    ).order_by(models.vw_TimeOffSummary.LeaveApplicationId.desc()).all()

@app.post("/RequestLeave", status_code=status.HTTP_201_CREATED)
async def request_leave(
    leave_in: models.LeaveRequestCreate, 
    current_user: Annotated[models.UserTable, Depends(get_current_user)],
    db: Session = Depends(get_payroll_db)
):
    try:
        # 1. Kunin ang HireDate at Last Record
        # Ginagamit natin ang query para makuha ang HireDate mula sa Employees table
        emp_data = db.execute(
            "SELECT HireDate FROM Employees WHERE EmployeeID = :id", 
            {"id": current_user.id}
        ).fetchone()

        last_record = db.query(models.vw_TimeOffSummary).filter(
            models.vw_TimeOffSummary.EmployeeID == current_user.id
        ).order_by(models.vw_TimeOffSummary.LeaveApplicationId.desc()).first()

        # 2. Re-calculate Earned Credits (Logic ni Gino Reyes)
        earned_credits = 0.0
        if emp_data and emp_data.HireDate:
            h_date = emp_data.HireDate
            c_year = date.today().year # 2026
            
            if c_year > h_date.year:
                if h_date.month <= 2:
                    earned_credits = 10.0
                else:
                    earned_credits = float(min(12 - h_date.month + 1, 10))

        # 3. Fallback values at Computation
        current_ending_balance = float(last_record.EndingBalance) if last_record else 0.0
        
        # Ang TOTAL AVAILABLE ay: (Dating Balance + Earned ngayong taon)
        # Babawasan lang natin ito ng mga nagamit na (Consumed) sa history
        total_earned_and_prev = current_ending_balance + earned_credits
        
        days_requested = float((leave_in.EndDate - leave_in.BeginDate).days + 1)

        # VALIDATION gamit ang updated calculation
        if days_requested > total_earned_and_prev:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient balance. Available: {total_earned_and_prev} credits."
            )

        # 4. New Available Balance
        new_available = total_earned_and_prev - days_requested

        # 5. Save Record
        new_leave = models.LeaveTable(
            EmployeeId=current_user.id,
            CompanyId=last_record.CompanyId if last_record else 1,
            DateCreated=datetime.now(timezone.utc).date(),
            BeginDate=leave_in.BeginDate,
            EndDate=leave_in.EndDate,
            TimeOffType=leave_in.TimeOffType,
            Description=leave_in.Description,
            UsedCredits=days_requested,
            ApprovalStatus="Pending",
            OpeningBalance=current_ending_balance, 
            EarnedCredits=earned_credits, # I-save na natin ang calculated earned credits
            EndingBalance=current_ending_balance, # Maintain base balance
            AvailableCredits=new_available 
        )

        db.add(new_leave)
        db.commit()

        return {"message": "Leave request submitted successfully."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/User/Me")
async def get_user_profile(
    current_user: Annotated[models.UserTable, Depends(get_current_user)],
    db_payroll: Session = Depends(get_payroll_db)
):
    from sqlalchemy import text
    
    # 1. Kunin ang HireDate
    emp_query = text("SELECT HireDate FROM Employees WHERE EmployeeID = :id")
    emp_result = db_payroll.execute(emp_query, {"id": current_user.id}).mappings().first()

    # 2. Kunin ang huling record
    last_record = db_payroll.query(models.vw_TimeOffSummary).filter(
        models.vw_TimeOffSummary.EmployeeID == current_user.id
    ).order_by(models.vw_TimeOffSummary.LeaveApplicationId.desc()).first()

    earned_credits = 0.0
    if emp_result and emp_result["HireDate"]:
        hire_date = emp_result["HireDate"]
        if isinstance(hire_date, str):
            hire_date = datetime.strptime(hire_date[:10], "%Y-%m-%d").date()
        elif isinstance(hire_date, datetime):
            hire_date = hire_date.date()
            
        current_year = 2026 
        if current_year > hire_date.year:
            hire_month = hire_date.month 
            earned_credits = 10.0 if hire_month <= 2 else float(12 - hire_month)
            earned_credits = max(0.0, min(earned_credits, 10.0))

    # --- BAGONG LOGIC PARA SA ENDING BALANCE ---
    # Ang starting pool ay ang Earned Credits (5) + anumang carry-over (kung meron)
    # Kung wala pang last_record, ang ending_bal ay equal sa earned_credits
    base_balance = float(last_record.EndingBalance) if last_record else earned_credits
    consumed = float(last_record.Consumed) if last_record else 0.0
    
    # EndingBalance should reflect current pool minus consumption
    current_ending_bal = base_balance - consumed
    available = current_ending_bal # Sa ngayon, parehas sila dahil earned logic ang gamit

    return {
        "id": current_user.id,
        "full_name": last_record.EmployeeName if last_record else current_user.full_name,
        "credits": {
            "ending_balance": available, # Gagawin nating 5 ito hangga't consumed is 0
            "earned": earned_credits,
            "consumed": consumed,
            "available": available,
        }
    }