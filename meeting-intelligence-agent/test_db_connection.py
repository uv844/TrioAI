"""
Test script to verify direct connection to Microsoft SQL Server / SSMS.
Run with: python test_db_connection.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

print("=" * 60)
print("SQL SERVER CONNECTION TEST")
print("=" * 60)

from app.database.session import SQLALCHEMY_DATABASE_URL, engine, Base
from app.models.meeting_db import MeetingModel

print(f"Target DB: {os.getenv('DB_NAME')}")
print(f"Target Server: {os.getenv('DB_SERVER')}")
print(f"Auth Mode: {'Windows Authentication' if os.getenv('USE_WINDOWS_AUTH', 'true').lower() == 'true' else 'SQL Server Auth'}")
print(f"Driver: {os.getenv('DB_DRIVER')}")
print("-" * 60)

try:
    print("Attempting to connect to SQL Server...")
    with engine.connect() as conn:
        print("[SUCCESS] Connected to SQL Server successfully!")

    print("Checking / creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] Table 'meetings' verified / created successfully!")

except Exception as err:
    print("\n[ERROR] Connection failed!")
    print(f"Details: {err}")
    print("\nTroubleshooting tips:")
    print("1. In SSMS, verify your exact Server Name (e.g. localhost, localhost\\SQLEXPRESS, or .\SQLEXPRESS).")
    print("2. Make sure the database exists in SSMS (or create it: CREATE DATABASE MeetingIntelligenceDB).")
    print("3. Check the settings in meeting-intelligence-agent/.env.")
print("=" * 60)

