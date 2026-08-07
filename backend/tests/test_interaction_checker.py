"""Tests for the interaction-check endpoint (run after load_interactions.py)."""
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_warfarin_aspirin_is_major():
    resp = client.post("/api/v1/prescription/interaction-check",
                       json={"patient_id": "P001",
                             "prescribed_drugs": ["warfarin", "aspirin"]})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["interactions"]) == 1
    assert body["interactions"][0]["severity"] == "MAJOR"


def test_amoxicillin_ibuprofen_no_conflict():
    resp = client.post("/api/v1/prescription/interaction-check",
                       json={"patient_id": "P001",
                             "prescribed_drugs": ["amoxicillin", "ibuprofen"]})
    body = resp.json()
    assert len(body["interactions"]) == 0
    assert set(body["safe"]) == {"amoxicillin", "ibuprofen"}


def test_simvastatin_clarithromycin_is_contraindicated():
    resp = client.post("/api/v1/prescription/interaction-check",
                       json={"patient_id": "P001",
                             "prescribed_drugs": ["simvastatin", "clarithromycin"]})
    body = resp.json()
    assert len(body["interactions"]) == 1
    assert body["interactions"][0]["severity"] == "CONTRAINDICATED"


def test_mixed_prescription_flags_each_pair_once():
    resp = client.post("/api/v1/prescription/interaction-check",
                       json={"patient_id": "P001",
                             "prescribed_drugs": ["warfarin", "aspirin", "amoxicillin"]})
    body = resp.json()
    # warfarin+aspirin (MAJOR) and warfarin+amoxicillin (MODERATE) -> 2 conflicts
    assert len(body["interactions"]) == 2
    # every listed drug is part of a flagged pair, so none are "safe"
    assert body["safe"] == []
    # amoxicillin appears in exactly one conflict (not double-flagged)
    involved = {(i["drug_a"], i["drug_b"]) for i in body["interactions"]}
    amox_pairs = [p for p in involved if "amoxicillin" in p]
    assert len(amox_pairs) == 1


def test_two_nsaids_flagged_once():
    # ibuprofen+naproxen is a curated exact pair (MODERATE)
    resp = client.post("/api/v1/prescription/interaction-check",
                       json={"patient_id": "P001",
                             "prescribed_drugs": ["ibuprofen", "naproxen"]})
    body = resp.json()
    assert len(body["interactions"]) == 1
    assert body["interactions"][0]["severity"] == "MODERATE"
