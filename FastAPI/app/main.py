from datetime import datetime, timedelta, timezone
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
# Import dependencies from database.py
from database import get_auth_db, get_payroll_db, pg_engine, BaseAuth

# --- 0. AUTO-CREATE POSTGRES TABLE ---
BaseAuth.metadata.create_all(bind=pg_engine)
print("Postgres sync complete.")

app = FastAPI(title="Leave Credit App")

# --- 1. MIDDLEWARE SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. SECURITY CONFIG ---
SECRET_KEY ="f34fb792147d3f5b418cebec18fd2b192b961b2acae5cdb1136f9dc5acc7ae52"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- 3. HELPER FUNCTIONS ---
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def get_user(db: Session, username: str):
    # Dito natin kukunin ang user sa Postgres (UserTable model)
    return db.query(models.UserTable).filter(models.UserTable.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- 4. DEPENDENCIES ---
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_auth_db) # Postgres for auth check
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
        
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# --- 5. ROUTES ---

# Public Route para sa Health Check
@app.get("/")
async def root():
    return {"message": "Leave Credit App API is running"}

# Login Route
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_auth_db) # Connects to Postgres
) -> models.Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return models.Token(access_token=access_token, token_type="bearer")

# Creating User Route
@app.post("/admin/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: models.UserInDB, 
    db: Session = Depends(get_auth_db)
):
    # Check if user already exists
    if get_user(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # SAve new user to Postgres
    new_user = models.UserTable(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.hashed_password), # HASHING
        disabled=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User {new_user.username} successfully created in Postgres"}

# Protected Route: Data from SQL Server
@app.get("/LeaveHistory")
async def get_leave_history(
    current_user: Annotated[models.UserTable, Depends(get_current_user)],
    db: Session = Depends(get_payroll_db) # Connects to SQL Server
):
    logged_in_id = current_user.id 

    user_data = db.query(models.vw_TimeOffSummary).filter(
        models.vw_TimeOffSummary.EmployeeID == logged_in_id
    ).all()

    # 3. Error Handling
    if not user_data:
        return []

    return user_data