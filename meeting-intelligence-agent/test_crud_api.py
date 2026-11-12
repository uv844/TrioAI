
import os
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

print("=" * 65)
print("FASTAPI + SQL SERVER CRUD TEST SUITE")
print("=" * 65)

# 0. Healthcheck
try:
    res = requests.get(f"{BASE_URL}/")
    print(f"[0] Server Healthcheck: Status {res.status_code}")
    print("    Response:", res.json())
except Exception as e:
    print("[!] FastAPI server is not reachable. Ensure uvicorn is running.")
    exit(1)

print("-" * 65)

# 1. CREATE (POST /meetings/)
print("[1] Testing CREATE meeting (POST /meetings/)...")
payload_1 = {
    "title": "Quarterly Product Strategy & Roadmap 2026",
    "transcript": "Discussed the release timeline for TrioAI agent intelligence modules. Agreed on prioritizing SSMS integration and cloud deployment by Q3."
}
res_create = requests.post(f"{BASE_URL}/meetings/", json=payload_1)
print(f"    Status: {res_create.status_code}")
created_data = res_create.json()
print("    Created:", json.dumps(created_data, indent=2))
meeting_id = created_data.get("id")

if not meeting_id:
    print("[ERROR] Failed to obtain meeting ID from create response.")
    exit(1)

print("-" * 65)

# 2. READ ALL (GET /meetings/)
print("[2] Testing READ ALL meetings (GET /meetings/)...")
res_all = requests.get(f"{BASE_URL}/meetings/")
print(f"    Status: {res_all.status_code}")
print(f"    Total records returned: {len(res_all.json())}")

print("-" * 65)

# 3. READ BY ID (GET /meetings/{id})
print(f"[3] Testing READ single meeting by ID (GET /meetings/{meeting_id})...")
res_one = requests.get(f"{BASE_URL}/meetings/{meeting_id}")
print(f"    Status: {res_one.status_code}")
print("    Record:", res_one.json())

print("-" * 65)

# 4. SEARCH (GET /meetings/search/?keyword=...)
print("[4] Testing SEARCH meetings (GET /meetings/search/?keyword=TrioAI)...")
res_search = requests.get(f"{BASE_URL}/meetings/search/", params={"keyword": "TrioAI"})
print(f"    Status: {res_search.status_code}")
print(f"    Matches found: {len(res_search.json())}")

print("-" * 65)

# 5. UPDATE (PUT /meetings/{id})
print(f"[5] Testing UPDATE meeting (PUT /meetings/{meeting_id})...")
update_payload = {
    "title": "Quarterly Product Strategy [UPDATED]",
    "transcript": "Updated transcript: Successfully tested SSMS connection and verified all database operations across all environments."
}
res_update = requests.put(f"{BASE_URL}/meetings/{meeting_id}", json=update_payload)
print(f"    Status: {res_update.status_code}")
print("    Updated:", res_update.json())

print("-" * 65)

# 6. DELETE (DELETE /meetings/{id})
print(f"[6] Testing DELETE meeting (DELETE /meetings/{meeting_id})...")
res_delete = requests.delete(f"{BASE_URL}/meetings/{meeting_id}")
print(f"    Status: {res_delete.status_code}")
print("    Delete response:", res_delete.json())

# Verify it was deleted (expecting 404)
res_verify_delete = requests.get(f"{BASE_URL}/meetings/{meeting_id}")
print(f"    Verification GET status (Expected 404): {res_verify_delete.status_code}")

print("=" * 65)
print("[COMPLETED] All CRUD operations tested!")
print("=" * 65)

