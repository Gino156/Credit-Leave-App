import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- POSTGRESQL (Auth) ---
pg_user = "postgres"
pg_pass = urllib.parse.quote_plus("dC_it@gn25?")
pg_host = "localhost"
pg_port = "5432"
pg_db   = "auth_db"

PG_DATABASE_URL = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
pg_engine = create_engine(PG_DATABASE_URL)
SessionAuth = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)

# ETO YUNG IMPORTANTE:
BaseAuth = declarative_base() 

# --- SQL SERVER (Payroll) ---
MSSQL_DATABASE_URL = (
    "mssql+pyodbc://./PayrollDB?"
    "driver=ODBC+Driver+18+for+SQL+Server&"
    "Trusted_Connection=yes&"
    "Encrypt=yes&"
    "TrustServerCertificate=yes"
)
ms_engine = create_engine(MSSQL_DATABASE_URL)
SessionPayroll = sessionmaker(autocommit=False, autoflush=False, bind=ms_engine)

# ETO PA YUNG ISA:
BasePayroll = declarative_base() 

# --- DEPENDENCIES ---
def get_auth_db():
    db = SessionAuth()
    try:
        yield db
    finally:
        db.close()

def get_payroll_db():
    db = SessionPayroll()
    try:
        yield db
    finally:
        db.close()