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
        # 1. Hanapin ang pinakahuling record (vw_TimeOffSummary)
        last_record = db.query(models.vw_TimeOffSummary).filter(
            models.vw_TimeOffSummary.EmployeeID == current_user.id
        ).order_by(models.vw_TimeOffSummary.LeaveApplicationId.desc()).first()

        # Fallback values kung bagong employee
        emp_company_id = last_record.CompanyId if last_record and last_record.CompanyId else 1
        current_ending_balance = float(last_record.EndingBalance) if last_record else 0.0
        current_available = float(last_record.AvailableCredits) if last_record else 0.0

        # 2. Compute Days Requested
        days_diff = (leave_in.EndDate - leave_in.BeginDate).days + 1
        
        # --- VALIDATION: Check kung sapat ang credits ---
        if days_diff > current_available:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient balance. You only have {current_available} credits left."
            )

        # 3. New Available Balance (Bawas agad kahit Pending)
        new_available = current_available - float(days_diff)

        # 4. Save Record
        new_leave = models.LeaveTable(
            EmployeeId=current_user.id,
            CompanyId=emp_company_id,
            DateCreated=datetime.now(timezone.utc).date(),
            BeginDate=leave_in.BeginDate,
            EndDate=leave_in.EndDate,
            TimeOffType=leave_in.TimeOffType,
            Description=leave_in.Description,
            UsedCredits=days_diff,
            ApprovalStatus="Pending",
            OpeningBalance=current_ending_balance, 
            EarnedCredits=0,
            EndingBalance=current_ending_balance,
            AvailableCredits=new_available 
        )

        db.add(new_leave)
        db.commit()

        return {"message": "Leave request submitted. Credits updated."}

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))