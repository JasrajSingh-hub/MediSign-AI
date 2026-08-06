"""Tests for the merged /prescription/audit endpoint (run after loaders)."""
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_audit_combines_allergy_and_interaction():
    # P001 allergic to Penicillins; warfarin+aspirin is a MAJOR interaction
    resp = client.post("/api/v1/prescription/audit",
                        json={"patient_id": "P001",
                              "prescribed_drugs": ["amoxicillin", "warfarin", "aspirin"]})
    assert resp.status_code == 200
    body = resp.json()

    # Allergy side: amoxicillin flagged, with alternative suggestions
    allergy_drugs = {c["drug"] for c in body["allergy"]["conflicts"]}
    assert "amoxicillin" in allergy_drugs
    assert body["allergy"]["conflicts"][0]["alternatives"]

    # Interaction side: warfarin+aspirin MAJOR present
    pairs = {(i["drug_a"], i["drug_b"]) for i in body["interactions"]["interactions"]}
    assert ("warfarin", "aspirin") in pairs

    # Top-level echo of the input list
    assert body["prescribed_drugs"] == ["amoxicillin", "warfarin", "aspirin"]


def test_audit_clean_prescription_has_no_conflicts():
    resp = client.post("/api/v1/prescription/audit",
                        json={"patient_id": "P001", "prescribed_drugs": ["ibuprofen"]})
    body = resp.json()
    assert body["allergy"]["conflicts"] == []
    assert body["interactions"]["interactions"] == []
