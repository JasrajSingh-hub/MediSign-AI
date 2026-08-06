"""Tests for the OCR scan pipeline (image -> text -> matched drugs -> audit).

Generates a synthetic printed prescription in-memory so the test needs no
fixture file. Requires the Tesseract binary to be installed.
"""
import io
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

import pytest
from PIL import Image, ImageDraw, ImageFont

from fastapi.testclient import TestClient
from main import app
from module_b_backend.app.modules.prescription.services import drug_matcher

client = TestClient(app)


def _make_prescription_png() -> bytes:
    img = Image.new("RGB", (700, 300), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        font = ImageFont.load_default()
    lines = [
        "Rx",
        "1. Amoxicillin 500mg - twice daily",
        "2. Warfarin 5mg - once daily",
        "3. Aspirin 75mg - once daily",
    ]
    y = 20
    for ln in lines:
        d.text((30, y), ln, fill="black", font=font)
        y += 55
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_matcher_ignores_noise_and_finds_drugs():
    text = "Rx Amoxicillin 500mg twice daily Warfarin 5mg"
    matched, _tokens = drug_matcher.match_drugs(text)
    names = {m["matched_drug"] for m in matched}
    assert "amoxicillin" in names
    assert "warfarin" in names
    # dosage/instruction words must not become drugs
    assert "twice" not in names and "daily" not in names


def test_matcher_resolves_brand_to_generic():
    # Augmentin is a brand for amoxicillin; Dolo is a brand for acetaminophen.
    text = "Rx Augmentin 625 twice daily Dolo 650 SOS"
    matched, _tokens = drug_matcher.match_drugs(text)
    by_generic = {m["matched_drug"]: m for m in matched}
    assert "amoxicillin" in by_generic
    assert by_generic["amoxicillin"]["brand"] == "augmentin"
    assert "acetaminophen" in by_generic


def test_ocr_audit_endpoint_reads_and_audits():
    png = _make_prescription_png()
    resp = client.post(
        "/api/v1/prescription/ocr-audit",
        data={"patient_id": "P001"},
        files={"image": ("rx.png", png, "image/png")},
    )
    assert resp.status_code == 200
    body = resp.json()

    read = set(body["prescribed_drugs"])
    assert "amoxicillin" in read, f"OCR missed amoxicillin: {body['raw_text']!r}"

    # amoxicillin should trigger the Penicillin allergy for P001
    allergy_drugs = {c["drug"] for c in body["audit"]["allergy"]["conflicts"]}
    assert "amoxicillin" in allergy_drugs
