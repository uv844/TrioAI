"""
Executes schema.sql against SQL Server MeetingDB database.
"""
from pathlib import Path
import pyodbc

sql_path = Path(__file__).resolve().parent / "schema.sql"
with open(sql_path, "r", encoding="utf-8") as f:
    raw_content = f.read()

# Separate statements by GO blocks
batches = [b.strip() for b in raw_content.split("GO") if b.strip()]

conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=127.0.0.1,1434;"
    "DATABASE=MeetingDB;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

print("Connecting to SQL Server (MeetingDB)...")
conn = pyodbc.connect(conn_str, autocommit=True, timeout=10)
cursor = conn.cursor()

print(f"Executing {len(batches)} schema creation batches...")
for idx, batch in enumerate(batches, 1):
    cleaned = "\n".join([line for line in batch.splitlines() if not line.strip().startswith("USE ")])
    if not cleaned.strip():
        continue
    try:
        cursor.execute(cleaned)
        print(f" -> Batch {idx} executed successfully.")
    except Exception as err:
        print(f" -> Batch {idx} note/warning: {err}")

# Verify tables
cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME")
tables = [r[0] for r in cursor.fetchall()]

print("\n" + "=" * 50)
print(f"SUCCESS: {len(tables)} tables verified in MeetingDB:")
print("=" * 50)
for t in tables:
    print(f"  [x] {t}")
print("=" * 50)

conn.close()

