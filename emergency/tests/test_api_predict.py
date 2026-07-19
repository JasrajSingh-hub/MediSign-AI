"""API /predict coverage (Phase 10 backfill): success, base64, and 422 paths."""
from __future__ import annotations

import base64

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

import api


@pytest.fixture
def client():
    return TestClient(api.app)


def test_predict_success_file(client, monkeypatch):
    monkeypatch.setattr(
        api,
        "predict_from_image_bytes",
        lambda data: {"available": True, "label": "help", "confidence": 0.9, "is_emergency": True},
    )
    r = client.post("/predict", files={"file": ("f.png", b"fake-bytes", "image/png")})
    assert r.status_code == 200
    assert r.json()["label"] == "help"


def test_predict_success_base64(client, monkeypatch):
    monkeypatch.setattr(
        api,
        "predict_from_image_bytes",
        lambda data: {"available": True, "label": "pain", "confidence": 0.8},
    )
    b64 = base64.b64encode(b"some-bytes").decode()
    # The endpoint mixes a file (multipart) and base64 field; base64 is supplied
    # as a form field (not a JSON body).
    r = client.post("/predict", data={"image_base64": b64})
    assert r.status_code == 200
    assert r.json()["label"] == "pain"


def test_predict_unavailable_422(client, monkeypatch):
    monkeypatch.setattr(
        api,
        "predict_from_image_bytes",
        lambda data: {"available": False, "error": "Could not decode image bytes"},
    )
    r = client.post("/predict", files={"file": ("f.png", b"not-an-image", "image/png")})
    assert r.status_code == 422
