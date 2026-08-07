"""Tests for the allergy-check endpoint (run after load_drug_classes.py)."""
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_penicillin_allergy_flags_amoxicillin():
    resp = client.post("/api/v1/prescription/allergy-check",
                        json={"patient_id": "P001", "prescribed_drugs": ["amoxicillin"]})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["conflicts"]) == 1
    assert body["conflicts"][0]["drug"] == "amoxicillin"


def test_class_level_match_flags_ampicillin():
    # ampicillin is ALSO a Penicillin -> must be caught by class match, not name match
    resp = client.post("/api/v1/prescription/allergy-check",
                        json={"patient_id": "P001", "prescribed_drugs": ["ampicillin"]})
    body = resp.json()
    assert len(body["conflicts"]) == 1
    assert body["conflicts"][0]["drug"] == "ampicillin"


def test_no_conflict_for_nsaid():
    resp = client.post("/api/v1/prescription/allergy-check",
                        json={"patient_id": "P001", "prescribed_drugs": ["ibuprofen"]})
    body = resp.json()
    assert len(body["conflicts"]) == 0


def test_mixed_prescription_only_flags_the_real_conflict():
    resp = client.post("/api/v1/prescription/allergy-check",
                        json={"patient_id": "P001",
                              "prescribed_drugs": ["amoxicillin", "ibuprofen", "warfarin"]})
    body = resp.json()
    conflicted = {c["drug"] for c in body["conflicts"]}
    assert conflicted == {"amoxicillin"}


def test_amoxicillin_conflict_suggests_azithromycin():
    # P001 allergic to Penicillins; amoxicillin is a Penicillin -> flag + suggest alt
    resp = client.post("/api/v1/prescription/allergy-check",
                        json={"patient_id": "P001", "prescribed_drugs": ["amoxicillin"]})
    body = resp.json()
    assert len(body["conflicts"]) == 1
    alt_drugs = {a["alternative_drug"] for a in body["conflicts"][0]["alternatives"]}
    assert "azithromycin" in alt_drugs


def test_dual_allergic_patient_filters_macrolide_alternative():
    # P002 allergic to BOTH Penicillins and Macrolides -> azithromycin must be excluded,
    # but clindamycin (Lincosamides) should still be suggested.
    from module_b_backend.app.modules.prescription import repository
    repository.add_patient_allergy("P002", "Penicillins", "Penicillin", "severe", "curated")
    repository.add_patient_allergy("P002", "Macrolides", "Azithromycin", "severe", "curated")
    resp = client.post("/api/v1/prescription/allergy-check",
                        json={"patient_id": "P002", "prescribed_drugs": ["amoxicillin"]})
    body = resp.json()
    assert len(body["conflicts"]) == 1
    alts = body["conflicts"][0]["alternatives"]
    alt_classes = {a["alternative_class"] for a in alts}
    assert "Macrolides" not in alt_classes          # azithromycin filtered out
    assert any(a["alternative_class"] == "Lincosamides" for a in alts)  # clindamycin remains
