import os
import io
import pytest
import numpy as np
import cv2
from PIL import Image
from fastapi.testclient import TestClient

# Set up testing environment variables before importing the app
os.environ["DB_PATH"] = "test_prescriptions.db"
os.environ["UPLOAD_DIR"] = "test_uploads"
os.environ["OCR_RATE_LIMIT_LIMIT"] = "100"
os.environ["OCR_RATE_LIMIT_WINDOW_SECONDS"] = "60"

# Make sure database is clean for tests
if os.path.exists("test_prescriptions.db"):
    try:
        os.remove("test_prescriptions.db")
    except Exception:
        pass

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ocr_service import app, UPLOAD_DIR, DB_PATH
from services.document_scanner import DocumentScannerService
from services.prescription_parser import PrescriptionParserService
from services.drug_safety import DrugSafetyService
from database import init_db

client = TestClient(app)

# Helper function to generate a dummy valid image in bytes
def generate_dummy_image(width=300, height=300, color=(255, 255, 255)) -> bytes:
    img = Image.new("RGB", (width, height), color)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()

@pytest.fixture(autouse=True)
def run_around_tests():
    # Setup test DB and directories
    init_db(DB_PATH)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield
    # Cleanup files in test uploads
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            try:
                os.remove(os.path.join(UPLOAD_DIR, f))
            except Exception:
                pass
        try:
            os.rmdir(UPLOAD_DIR)
        except Exception:
            pass
    # Clean test DB
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass

# =====================================================================
# SERVICE UNIT TESTS
# =====================================================================

def test_document_scanner_fallback():
    """Verify that scanner service falls back gracefully on low-contrast/plain images."""
    scanner = DocumentScannerService()
    # Create plain white image
    img = np.ones((400, 400, 3), dtype=np.uint8) * 255
    
    detection = scanner.detect_document(img)
    # Plain image should not have sharp borders, so it will fall back or return not detected
    # We test that detect_document runs without crashing
    assert "detected" in detection
    
    # Perspective correction on empty points should return original image
    corrected = scanner.correct_perspective(img, None)
    assert np.array_equal(corrected, img)

def test_document_scanner_enhancement():
    """Verify scanner enhancement works on sample numpy arrays."""
    scanner = DocumentScannerService()
    img = np.ones((200, 200, 3), dtype=np.uint8) * 128
    enhanced = scanner.enhance_document(img)
    # Output should be single-channel grayscale (enhanced)
    assert len(enhanced.shape) == 2 or enhanced.shape[2] == 1
    assert enhanced.shape[0] == 200
    assert enhanced.shape[1] == 200

def test_prescription_parser_accuracy():
    """Verify parser extracts metadata and medicines correctly using regex."""
    parser = PrescriptionParserService()
    sample_text = """
    City General Hospital
    Dr. Rajesh Kumar, MD
    Reg No: 12345
    
    Patient Name: Amit Sharma
    Age: 35 Yrs    Gender: Male
    Date: 24/06/2026
    
    Rx:
    1. Paracetamol 500mg TDS for 5 days (after food)
    2. Amoxicillin 250 mg twice daily for 7 days
    3. Ibuprofen 400mg when required
    """
    
    result = parser.parse(sample_text)
    
    assert result["doctor_name"] == "Rajesh Kumar"
    assert result["hospital_name"] == "City General Hospital"
    assert result["patient_name"] == "Amit Sharma"
    assert result["age"] == "35"
    assert result["gender"] == "Male"
    assert result["date"] == "24/06/2026"
    
    medicines = result["medicines"]
    assert len(medicines) == 3
    
    # Paracetamol
    assert medicines[0]["name"] == "Paracetamol"
    assert medicines[0]["dose"] == "500mg"
    assert medicines[0]["frequency"] == "Thrice Daily"
    assert medicines[0]["duration"] == "5 days"
    assert medicines[0]["instructions"] == "After Food"
    
    # Amoxicillin
    assert medicines[1]["name"] == "Amoxicillin"
    assert medicines[1]["dose"] == "250 mg"
    assert medicines[1]["frequency"] == "Twice Daily"
    assert medicines[1]["duration"] == "7 days"
    
    # Ibuprofen
    assert medicines[2]["name"] == "Ibuprofen"
    assert medicines[2]["dose"] == "400mg"
    assert medicines[2]["frequency"] == "As Needed"

def test_drug_safety_verification():
    """Verify drug safety flags missing details, duplicates, and spelling errors."""
    safety = DrugSafetyService()
    
    # Sample data with duplicates, missing dosage, and spelling errors
    parsed_data = {
        "medicines": [
            {"name": "Paracetamol", "dose": "", "frequency": "Twice Daily"},
            {"name": "Ibuprofen", "dose": "400mg", "frequency": ""},
            {"name": "Paracetamol", "dose": "500mg", "frequency": "Once Daily"},
            {"name": "Pa1acetam0l", "dose": "500mg", "frequency": "Once Daily"}
        ]
    }
    
    # Low confidence OCR (0.45)
    warnings = safety.check_safety(parsed_data, 0.45)
    
    # Warnings should include:
    # 1. Low confidence warning
    # 2. Dosage missing for Paracetamol
    # 3. Frequency missing for Ibuprofen
    # 4. Duplicate Paracetamol
    # 5. Suspicious spelling of Pa1acetam0l
    assert any("Low overall OCR confidence" in w for w in warnings)
    assert any("Dosage missing for medication: 'Paracetamol'" in w for w in warnings)
    assert any("Frequency details missing for medication: 'Ibuprofen'" in w for w in warnings)
    assert any("Duplicate medication detected: 'Paracetamol'" in w for w in warnings)
    assert any("Suspicious characters detected in medication name: 'Pa1acetam0l'" in w for w in warnings)

# =====================================================================
# API ENDPOINT TESTS
# =====================================================================

def test_health_check():
    """Verify health endpoint."""
    response = client.get("/api/v1/prescription/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload_success():
    """Verify uploading a valid image returns a session ID."""
    dummy_png = generate_dummy_image()
    response = client.post(
        "/api/v1/prescription/upload",
        files={"file": ("test.png", dummy_png, "image/png")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "session_id" in data
    assert data["image_name"].startswith(data["session_id"])
    
    # Verify file saved on disk
    filepath = os.path.join(UPLOAD_DIR, data["image_name"])
    assert os.path.exists(filepath)

def test_upload_invalid_mime():
    """Verify that uploading PDFs, ZIPs, or EXEs is rejected."""
    bad_files = [
        ("test.pdf", b"%PDF-1.4", "application/pdf"),
        ("test.zip", b"PK\x03\x04", "application/zip"),
        ("test.exe", b"MZ", "application/octet-stream")
    ]
    for filename, content, mime in bad_files:
        response = client.post(
            "/api/v1/prescription/upload",
            files={"file": (filename, content, mime)}
        )
        assert response.status_code == 400
        assert "Unsupported file format" in response.json()["detail"]

def test_upload_empty_file():
    """Verify empty uploads are rejected."""
    response = client.post(
        "/api/v1/prescription/upload",
        files={"file": ("empty.png", b"", "image/png")}
    )
    assert response.status_code == 400
    assert "Uploaded file is empty" in response.json()["detail"]

def test_upload_oversized_file():
    """Verify oversized files are rejected (10MB+)."""
    oversized = b"\x00" * (10 * 1024 * 1024 + 10)
    response = client.post(
        "/api/v1/prescription/upload",
        files={"file": ("oversized.png", oversized, "image/png")}
    )
    assert response.status_code == 413
    assert "exceeds the maximum limit" in response.json()["detail"]

def test_upload_small_dimensions():
    """Verify images with small dimensions (<100x100) are rejected."""
    small_img = generate_dummy_image(width=50, height=50)
    response = client.post(
        "/api/v1/prescription/upload",
        files={"file": ("small.png", small_img, "image/png")}
    )
    assert response.status_code == 400
    assert "Image dimensions are too small" in response.json()["detail"]

def test_process_invalid_request():
    """Verify process endpoint rejects requests without session_id or file."""
    response = client.post("/api/v1/prescription/process")
    assert response.status_code == 400
    assert "Either session_id or file must be provided" in response.json()["detail"]

def test_process_flow_success(monkeypatch):
    """Verify end-to-end OCR processing workflow with mock OCR service."""
    # Mock OCRService.extract_text to prevent loading/downloading actual model weights in tests
    mock_ocr_text = "City Hospital\nDr. Rajesh\nPatient: Amit\nParacetamol 500mg BD"
    
    def mock_extract_text(self, image):
        return {
            "text": mock_ocr_text,
            "confidence": 0.88,
            "regions": [
                {"bbox": [[0,0],[100,0],[100,20],[0,20]], "text": "Paracetamol 500mg BD", "confidence": 0.88}
            ]
        }
    
    from services.ocr_service import OCRService
    monkeypatch.setattr(OCRService, "extract_text", mock_extract_text)

    # 1. Upload first
    dummy_png = generate_dummy_image()
    up_resp = client.post(
        "/api/v1/prescription/upload",
        files={"file": ("test.png", dummy_png, "image/png")}
    )
    assert up_resp.status_code == 200
    session_id = up_resp.json()["session_id"]
    
    # 2. Process
    proc_resp = client.post(
        "/api/v1/prescription/process",
        data={"session_id": session_id, "uploaded_by": "Dr. Test"}
    )
    assert proc_resp.status_code == 200
    res_data = proc_resp.json()
    assert res_data["success"] is True
    assert "id" in res_data
    assert res_data["session_id"] == session_id
    assert "Paracetamol" in res_data["raw_text"]
    assert res_data["structured_data"]["patient_name"] == "Amit"
    assert len(res_data["structured_data"]["medicines"]) == 1
    assert res_data["confidence"] == 0.88

    # Verify file is cleaned up after process
    filepath = os.path.join(UPLOAD_DIR, up_resp.json()["image_name"])
    assert not os.path.exists(filepath)

    # 3. Retrieve by ID
    get_resp = client.get(f"/api/v1/prescription/{res_data['id']}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["success"] is True
    assert get_data["data"]["uploaded_by"] == "Dr. Test"
    assert get_data["data"]["raw_text"] == mock_ocr_text
    assert get_data["data"]["confidence"] == 0.88

def test_process_direct_upload_success(monkeypatch):
    """Verify processing works with direct image file upload."""
    mock_ocr_text = "City Clinic\nDr. Kumar\nPatient: John\nAmoxicillin 250mg TDS for 5 days"
    
    def mock_extract_text(self, image):
        return {
            "text": mock_ocr_text,
            "confidence": 0.92,
            "regions": []
        }
    
    from services.ocr_service import OCRService
    monkeypatch.setattr(OCRService, "extract_text", mock_extract_text)

    dummy_png = generate_dummy_image()
    response = client.post(
        "/api/v1/prescription/process",
        files={"file": ("direct.png", dummy_png, "image/png")},
        data={"uploaded_by": "Nurse Sally"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert "id" in res_data
    assert res_data["structured_data"]["doctor_name"] == "Kumar"
    assert res_data["structured_data"]["patient_name"] == "John"
    assert len(res_data["structured_data"]["medicines"]) == 1
    assert res_data["structured_data"]["medicines"][0]["name"] == "Amoxicillin"

    # Verify ID exists in database
    get_resp = client.get(f"/api/v1/prescription/{res_data['id']}")
    assert get_resp.status_code == 200
