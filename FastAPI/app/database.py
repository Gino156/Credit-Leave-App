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

BaseAuth = declarative_base() 

# --- SQL SERVER (Payroll) ---
sql_user = "devsa"
sql_pass = urllib.parse.quote_plus("Ftp@2024?")
sql_host = "172.96.10.78"

# Dito natin bubuuin ang URL variable na hinahanap ng main.py
MSSQL_DATABASE_URL = (
    f"mssql+pyodbc://{sql_user}:{sql_pass}@{sql_host}/PayrollDB"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

# Gamitin ang variable na MSSQL_DATABASE_URL
ms_engine = create_engine(MSSQL_DATABASE_URL, fast_executemany=True)
SessionPayroll = sessionmaker(autocommit=False, autoflush=False, bind=ms_engine)

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