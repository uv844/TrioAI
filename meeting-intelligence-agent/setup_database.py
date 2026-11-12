"""
Automated script to:
1. Connect to SQL Server master database.
2. Check if 'MeetingIntelligenceDB' exists; if not, create it.
3. Initialize the 'meetings' table.
4. Verify by reading the table structure.
"""
import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv
import pyodbc
from sqlalchemy import create_engine, inspect

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_NAME = os.getenv("DB_NAME", "MeetingIntelligenceDB")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
USE_WINDOWS_AUTH = os.getenv("USE_WINDOWS_AUTH", "true").strip().lower() in ("true", "1", "yes")

print("=" * 60)
print("SQL SERVER DATABASE CREATION & SETUP SCRIPT")
print("=" * 60)
print(f"Target Server : {DB_SERVER}")
print(f"Database Name : {DB_NAME}")
print(f"Driver        : {DB_DRIVER}")
print(f"Auth Type     : {'Windows Authentication' if USE_WINDOWS_AUTH else 'SQL Server Auth'}")
print("-" * 60)

# Step 1: Connect to master to check/create the database
if USE_WINDOWS_AUTH:
    master_conn_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        "DATABASE=master;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
else:
    DB_USER = os.getenv("DB_USER", "sa")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    master_conn_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        "DATABASE=master;"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        "TrustServerCertificate=yes;"
    )

try:
    print("[1/3] Connecting to SQL Server (master database)...")
    conn = pyodbc.connect(master_conn_str, autocommit=True, timeout=5)
    cursor = conn.cursor()
    print("      Connected successfully.")

    # Check if DB exists
    cursor.execute(f"SELECT database_id FROM sys.databases WHERE name = '{DB_NAME}'")
    row = cursor.fetchone()
    if not row:
        print(f"[2/3] Database '{DB_NAME}' does not exist. Creating it now...")
        cursor.execute(f"CREATE DATABASE [{DB_NAME}]")
        print(f"      Database '{DB_NAME}' created successfully.")
    else:
        print(f"[2/3] Database '{DB_NAME}' already exists.")
    conn.close()

    # Step 2: Use SQLAlchemy to create tables
    print(f"[3/3] Initializing tables in '{DB_NAME}'...")
    from app.database.session import engine, Base
    from app.models.meeting_db import MeetingModel

    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"      Tables currently present: {tables}")
    if "meetings" in tables:
        print("      Table 'meetings' is ready to use!")

    print("\n[SUCCESS] Everything is set up and connected successfully!")

except Exception as ex:
    print(f"\n[FAILED] Could not connect or create database.")
    print(f"Error details: {ex}")
    print("\nNext step: If the SQL Server service is stopped, start it in Windows Services (services.msc) and re-run this script.")

print("=" * 60)

