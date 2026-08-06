"""Live verification test for the Triage Question System and Reasoning Cache."""
import json
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def print_section(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def test_live_scenarios():
    print_section("SCENARIO 1: Emergency Sign = AMBULANCE (Instant Critical)")
    res1 = client.post("/triage/context", json={"patient_id": "P001", "emergency_sign": "AMBULANCE"})
    print(f"Status: {res1.status_code}")
    print(json.dumps(res1.json(), indent=2))

    print_section("SCENARIO 2: Emergency Sign = HEART (No Prescription)")
    res2 = client.post("/triage/context", json={"patient_id": "P001", "emergency_sign": "HEART"})
    print(f"Status: {res2.status_code}")
    print(json.dumps(res2.json(), indent=2))

    print_section("SCENARIO 3: Emergency Sign = BREATHING + Salbutamol Prescription")
    res3 = client.post("/triage/context", json={
        "patient_id": "P001",
        "emergency_sign": "BREATHING",
        "drugs": ["salbutamol"]
    })
    print(f"Status: {res3.status_code}")
    print(json.dumps(res3.json(), indent=2))

    print_section("SCENARIO 4: medPaper Uploaded (Paracetamol + Azithromycin)")
    res4 = client.post("/triage/context", json={
        "patient_id": "P001",
        "drugs": ["paracetamol", "azithromycin"]
    })
    print(f"Status: {res4.status_code}")
    data4 = res4.json()
    print(json.dumps(data4, indent=2))

    print_section("SCENARIO 5: 2nd Call for medPaper (Verifying Cache HIT)")
    res5 = client.post("/triage/context", json={
        "patient_id": "P001",
        "drugs": ["paracetamol", "azithromycin"]
    })
    data5 = res5.json()
    print(f"Cache Hit: {data5['cache_hit']} | Cache Type: {data5['cache_type']}")
    print(f"Signature: {data5['signature']}")

    print_section("SCENARIO 6: Doctor Handoff Summary Generation")
    res6 = client.post("/triage/summary", json={
        "patient_id": "P001",
        "drugs": ["paracetamol", "azithromycin"],
        "context": "Respiratory Infection",
        "answers": {
            "fever": "Yes",
            "fever_duration": "3 Days or more",
            "cough": "Yes"
        }
    })
    print(f"Status: {res6.status_code}")
    print(json.dumps(res6.json(), indent=2))


if __name__ == "__main__":
    test_live_scenarios()
