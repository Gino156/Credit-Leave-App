##Validation Layer##

from pydantic import BaseModel
from typing import Optional

class LeaveDetails(BaseModel):
    employee_name: str
    reason_of_leave: Optional[str] = None
    date: str
    file_date: int
    starts_with: str
    ends_with: str
    status: str