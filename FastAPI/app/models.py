from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, Text
from database import BasePayroll, BaseAuth
from pydantic import BaseModel

# --- SQL SERVER MODELS (Binds to BasePayroll) ---
class LeaveTable(BasePayroll):
    __tablename__ = "LeaveApplication" # Siguraduhing tugma sa actual table name sa SQL Server
    LeaveApplicationId = Column(Integer, primary_key=True, index=True) 
    EmployeeId = Column(Integer)
    DateCreated = Column(Date)
    BeginDate = Column(Date)
    EndDate = Column(Date)
    ApprovalStatus = Column(String) 
    Description = Column(Text)
    UsedCredits = Column(Integer)
    # Idagdag ang mga bagong columns dito para sa table mapping
    OpeningBalance = Column(Numeric)
    EarnedCredits = Column(Numeric)
    EndingBalance = Column(Numeric)
    AvailableCredits = Column(Numeric)

class vw_TimeOffSummary(BasePayroll):
    __tablename__ = "vw_TimeOffSummary"
    LeaveApplicationId = Column(Integer, primary_key=True, index=True)
    EmployeeID = Column(Integer, index=True) # Ito ang gagamitin sa filter (current_user.id)
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
    # Dapat tugma ang mga ito sa column names sa iyong SQL View script
    OpeningBalance = Column(Integer)
    EarnedCredits = Column(Integer) # In-update mula sa 'Earned'
    EndingBalance = Column(Integer)
    AvailableCredits = Column(Integer) # In-update mula sa 'Available'

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