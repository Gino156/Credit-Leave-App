from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = (
    "mssql+pyodbc://./PayrollDB?"
    "driver=ODBC+Driver+18+for+SQL+Server&"
    "Trusted_Connection=yes&"
    "Encrypt=yes&"
    "TrustServerCertificate=yes"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()