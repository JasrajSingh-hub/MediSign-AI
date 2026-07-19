"""Integration tests for the FastAPI service (Phase 9).

Require FastAPI. Skipped automatically when absent. When installed: the health,
status, Swagger/OpenAPI, and request-validation endpoints are exercised without
needing OpenCV/MediaPipe or a trained model (which only the /predict happy path
requires).
"""
from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

import api


@pytest.fixture(scope="module")
def client():
    return TestClient(api.app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_status(client):
    r = client.get("/status")
    assert r.status_code == 200
    j = r.json()
    assert "classes" in j and "model_loaded" in j
    assert isinstance(j["classes"], list)


def test_openapi_lists_predict(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "/predict" in r.json()["paths"]


def test_docs_ui(client):
    r = client.get("/docs")
    assert r.status_code == 200


def test_predict_without_image_400(client):
    r = client.post("/predict", json={})
    assert r.status_code == 400
