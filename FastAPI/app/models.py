from datetime import date
from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, Text
from database import BasePayroll, BaseAuth
from pydantic import BaseModel

# --- SQL SERVER MODELS (Binds to BasePayroll) ---
class LeaveTable(BasePayroll):
    __tablename__ = "LeaveApplication"

    __table_args__ = {"implicit_returning": False}

    LeaveApplicationId = Column(Integer, primary_key=True, index=True) 
    EmployeeId = Column(Integer)
    DateCreated = Column(Date)
    BeginDate = Column(Date)
    EndDate = Column(Date)
    ApprovalStatus = Column(String) 
    Description = Column(Text)
    UsedCredits = Column(Integer)
    TimeOffType = Column(String)
    OpeningBalance = Column(Numeric, default=0)
    EarnedCredits = Column(Numeric, default=0)
    EndingBalance = Column(Numeric, default=0)
    AvailableCredits = Column(Numeric, default=0)
    LeaveApplicationId = Column(Integer, primary_key=True, index=True)
    EmployeeId = Column(Integer)
    CompanyId = Column(Integer)

class vw_TimeOffSummary(BasePayroll):
    #must match the column names in SQL Server
    __tablename__ = "vw_TimeOffSummary"
    LeaveApplicationId = Column(Integer, primary_key=True, index=True)
    EmployeeID = Column(Integer, index=True) 
    DateCreated = Column(Date)
    BeginDate = Column(Date)
    EndDate = Column(Date)
    EmployeeName = Column(String)
    Consumed = Column(Integer)
    Description = Column(String)
    TimeOffType = Column(String)
    ApprovalStatus = Column(String)
    Year = Column(Integer)
    CompanyId = Column(Integer)
    CompanyName = Column(String)
    CompanyCode = Column(String)
    OpeningBalance = Column(Integer)
    EarnedCredits = Column(Integer)
    EndingBalance = Column(Integer)
    AvailableCredits = Column(Integer) 

# --- POSTGRESQL MODELS (Binds to BaseAuth) ---
class UserTable(BaseAuth):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)

# --- PYDANTIC MODELS (Schemas) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

    # Idagdag ito sa dulo ng models.py
class LeaveRequestCreate(BaseModel):
    TimeOffType: str
    BeginDate: date
    EndDate: date
    Description: str