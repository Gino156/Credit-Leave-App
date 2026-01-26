from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import get_db
import models

app = FastAPI()

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/employees")
async def get_employees(db: Session = Depends(get_db)):
    employees = db.query(models.LeaveTable).all()
    return employees

@app.get("/sample")
async def get_sample():
    return {"message": "Initializing FTP Web App..."}

@app.get("/")
async def testing():
    return {"message": "Welcome to the Leave Credit App"}

@app.get("/LeaveHistory")
async def get_leave_history(db: Session = Depends(get_db)):
    leave_history = db.query(models.vw_TimeOffSummary).all()
    return leave_history

