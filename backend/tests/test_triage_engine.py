"""Unit tests for the Triage Engine and Two-Tier Reasoning Cache (Phases 1-9)."""
from fastapi.testclient import TestClient
from main import app
from module_b_backend.app.modules.triage.services import cache_service, context_builder, rule_engine

client = TestClient(app)


def test_context_builder():
    """Verify local SQLite context_builder aggregates indications and symptoms."""
    ctx = context_builder.build_clinical_context(["paracetamol", "azithromycin"])
    assert "Paracetamol" in ctx["prescribed_drugs"]
    assert "Azithromycin" in ctx["prescribed_drugs"]
    assert "Respiratory Infection" in ctx["therapeutic_domains"] or "Pain & Fever" in ctx["therapeutic_domains"]
    assert len(ctx["aggregated_indications"]) > 0


def test_cache_signature_hashing():
    """Verify SHA256 signature generation is deterministic and order-insensitive."""
    sig1 = cache_service.generate_exact_signature(["paracetamol", "azithromycin", "pantoprazole"])
    sig2 = cache_service.generate_exact_signature(["Pantoprazole", "AZITHROMYCIN", "Paracetamol "])
    assert sig1 == sig2
    assert len(sig1) == 16

    dom_sig1 = cache_service.generate_domain_signature(["Pain & Fever", "Respiratory Infection"])
    dom_sig2 = cache_service.generate_domain_signature(["respiratory infection ", "pain & fever"])
    assert dom_sig1 == dom_sig2


def test_rule_engine_prioritization():
    """Verify rule engine priority calculation and red flag detection."""
    # Low priority
    pri_low, alert_low, _ = rule_engine.evaluate_triage_priority(
        {"fever": "Yes", "fever_duration": "1 Day"}
    )
    assert pri_low == "LOW"
    assert alert_low is False

    # Medium priority (persistent fever + cough)
    pri_med, alert_med, _ = rule_engine.evaluate_triage_priority(
        {"fever": "Yes", "fever_duration": "3 Days or more", "cough": "Yes"}
    )
    assert pri_med == "MEDIUM"
    assert alert_med is False

    # High priority (red flag)
    pri_high, alert_high, flags = rule_engine.evaluate_triage_priority(
        {"difficulty_breathing": "Yes", "chest_pain": "Yes"}
    )
    assert pri_high == "HIGH"
    assert alert_high is True
    assert len(flags) > 0


def test_triage_context_endpoint_and_cache():
    """Test POST /triage/context endpoint and verify reasoning cache hit on 2nd call."""
    payload = {
        "patient_id": "P001",
        "drugs": ["paracetamol", "azithromycin", "pantoprazole"]
    }
    
    # 1st call (Generates context and populates cache)
    resp1 = client.post("/triage/context", json=payload)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["patient_id"] == "P001"
    assert len(data1["contexts"]) > 0
    assert len(data1["question_tree"]) > 0

    # 2nd call (Must be a Cache HIT!)
    resp2 = client.post("/triage/context", json=payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["cache_hit"] is True
    assert data2["cache_type"] in ("exact_hit", "domain_hit")
    assert data2["signature"] == data1["signature"]


def test_triage_summary_endpoint():
    """Test POST /triage/summary endpoint."""
    payload = {
        "patient_id": "P001",
        "drugs": ["paracetamol", "azithromycin"],
        "context": "Respiratory Infection",
        "answers": {
            "fever": "Yes",
            "fever_duration": "3 Days or more",
            "cough": "Yes"
        }
    }
    resp = client.post("/triage/summary", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["patient_id"] == "P001"
    assert data["priority"] == "MEDIUM"
    assert len(data["doctor_summary"]) > 0
    assert "Paracetamol" in data["doctor_summary"] or "paracetamol" in data["doctor_summary"].lower()


def test_emergency_sign_ambulance_instant_critical():
    """Verify AMBULANCE sign triggers instant_critical bypass without questions."""
    payload = {"patient_id": "P001", "emergency_sign": "AMBULANCE"}
    resp = client.post("/triage/context", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["instant_critical"] is True
    assert len(data["question_tree"]) == 0


def test_emergency_sign_breathing_with_prescription():
    """Verify BREATHING sign + Salbutamol prescription generates inhaler-aware questions."""
    payload = {
        "patient_id": "P001",
        "drugs": ["salbutamol"],
        "emergency_sign": "BREATHING"
    }
    resp = client.post("/triage/context", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["instant_critical"] is False
    assert len(data["question_tree"]) > 0
    assert "inhaler" in data["question_tree"][0]["question"].lower()


def test_emergency_sign_knee_without_prescription():
    """Verify KNEE sign without prescription generates generic knee questions."""
    payload = {"patient_id": "P001", "emergency_sign": "KNEE"}
    resp = client.post("/triage/context", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["instant_critical"] is False
    assert len(data["question_tree"]) > 0
    assert "knee" in data["question_tree"][0]["question"].lower()

