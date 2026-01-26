from sqlalchemy import Column, Integer, String, Date
from database import Base

class LeaveTable(Base):
    __tablename__ = "LeaveTable"

    LeaveId = Column(Integer, primary_key=True, index=True) 
    EmployeeId = Column(Integer)
    FileDate = Column(Date)
    BeginDate = Column(Date)
    EndDate = Column(Date)
    LeaveStatus = Column(String) 
    ReasonOfLeave = Column(String)
    LeaveYear = Column(Integer)
    Consume = Column(Integer)
    AvailableBalance = Column(Integer)

class vw_TimeOffSummary(Base):
    __tablename__ = "vw_TimeOffSummary"

    LeaveApplicationId = Column(Integer, primary_key=True, index=True)
    EmployeeID = Column(Integer, index=True)
    DateCreated= Column(Date)
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
    Earned = Column(Integer)
    EndingBalance = Column(Integer)
    Available = Column(Integer)