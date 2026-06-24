import os
import io
import uuid
import time
import shutil
import logging
import sqlite3
from collections import defaultdict
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Request, UploadFile, File, BackgroundTasks, Form, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import cv2
import numpy as np
from PIL import Image

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ocr_service")

# Resolve DB and Upload directories relative to file location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.getenv("DB_PATH", "prescriptions.db")
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(BASE_DIR, DB_PATH)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "temp_uploads")
if not os.path.isabs(UPLOAD_DIR):
    UPLOAD_DIR = os.path.join(BASE_DIR, UPLOAD_DIR)

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize services
from services.document_scanner import DocumentScannerService
from services.ocr_service import OCRService
from services.prescription_parser import PrescriptionParserService
from services.drug_safety import DrugSafetyService
from database import init_db, save_prescription, get_prescription

scanner_service = DocumentScannerService()
ocr_service = OCRService()
parser_service = PrescriptionParserService()
safety_service = DrugSafetyService()

# Automatically initialize database on startup
init_db(DB_PATH)

router = APIRouter()

# =====================================================================
# IN-MEMORY RATE LIMITER (reused pattern from tts_service)
# =====================================================================
class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.history = defaultdict(list)

    def check_rate_limit(self, client_id: str):
        now = time.time()
        # Evict old timestamps
        self.history[client_id] = [
            t for t in self.history[client_id] if now - t < self.window_seconds
        ]
        if len(self.history[client_id]) >= self.limit:
            logger.warning(f"Rate limit hit for client: {client_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded for OCR requests. Please try again later."
            )
        self.history[client_id].append(now)

rate_limiter = InMemoryRateLimiter(
    limit=int(os.getenv("OCR_RATE_LIMIT_LIMIT", "30")),
    window_seconds=int(os.getenv("OCR_RATE_LIMIT_WINDOW_SECONDS", "60"))
)

# =====================================================================
# SECURITY & VALIDATION HELPERS
# =====================================================================
def validate_file_metadata(filename: str, content_type: str):
    """Rejects disallowed file types based on name extension and content-type."""
    if not filename:
        raise HTTPException(status_code=400, detail="Filename missing.")

    ext = os.path.splitext(filename.lower())[1]
    allowed_exts = {".jpg", ".jpeg", ".png"}
    allowed_mimes = {"image/jpeg", "image/jpg", "image/png"}

    if ext not in allowed_exts or content_type not in allowed_mimes:
        logger.warning(f"Validation failed: Rejected file {filename} with MIME type {content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only JPG, JPEG, and PNG images are allowed."
        )

async def validate_file_content(file: UploadFile) -> bytes:
    """Validates file size and image dimensions."""
    content = await file.read()
    file_size = len(content)
    await file.seek(0)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Max 10MB limit
    MAX_FILE_SIZE = 10 * 1024 * 1024
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"Validation failed: Rejected file of size {file_size} bytes.")
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File size exceeds the maximum limit of 10 MB."
        )

    try:
        # Validate dimensions using Pillow
        img = Image.open(io.BytesIO(content))
        width, height = img.size
        
        # Enforce minimum dimension
        if width < 100 or height < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image dimensions are too small. Minimum resolution is 100x100 pixels."
            )
            
        # Guard against massive images to prevent OOM
        if width > 10000 or height > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image dimensions exceed the safety limit of 10000x10000 pixels."
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Validation failed: Image is corrupted or unreadable. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image structure or file is corrupted."
        )

    return content

def cleanup_file(filepath: str):
    """Utility to safely remove temporary files from storage."""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Temporary file cleaned up: {filepath}")
    except Exception as e:
        logger.error(f"Error cleaning up temporary file {filepath}: {e}")

# =====================================================================
# API ENDPOINTS
# =====================================================================

@router.get("/api/v1/prescription/health")
async def health_check():
    """Simple status check reporting backend availability."""
    return {"status": "healthy", "service": "Prescription OCR Service"}

@router.post("/api/v1/prescription/upload")
async def upload_prescription(
    request: Request,
    file: UploadFile = File(...)
):
    """
    Validates and stores the prescription image temporarily.
    Returns a unique session_id to identify this session.
    """
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check_rate_limit(client_ip)

    # 1. Validate file format and content-type headers
    validate_file_metadata(file.filename, file.content_type)

    # 2. Validate file size and image resolution limits
    await validate_file_content(file)

    session_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename.lower())[1]
    saved_filename = f"{session_id}{file_ext}"
    saved_filepath = os.path.join(UPLOAD_DIR, saved_filename)

    logger.info(f"Uploading file {file.filename} for session {session_id} from IP {client_ip}")

    try:
        with open(saved_filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "success": True,
            "session_id": session_id,
            "image_name": saved_filename
        }
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        # Make sure to clean up if partial write occurred
        cleanup_file(saved_filepath)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file."
        )

@router.post("/api/v1/prescription/process")
async def process_prescription(
    request: Request,
    background_tasks: BackgroundTasks,
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    uploaded_by: str = Form("worker")
):
    """
    Performs full OCR workflow on a prescription image.
    Can accept a session_id (of a previously uploaded image) OR a direct image file upload.
    Runs Preprocessing -> Boundary Detection -> Perspective Warp -> Image Enhancement -> OCR -> Parser -> Safety Check.
    """
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check_rate_limit(client_ip)

    filepath = None
    image_name = ""
    resolved_session_id = session_id

    # 1. Resolve image source
    if file:
        # Direct Upload
        validate_file_metadata(file.filename, file.content_type)
        await validate_file_content(file)

        if not resolved_session_id:
            resolved_session_id = str(uuid.uuid4())
        
        file_ext = os.path.splitext(file.filename.lower())[1]
        image_name = f"{resolved_session_id}{file_ext}"
        filepath = os.path.join(UPLOAD_DIR, image_name)

        try:
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            logger.error(f"Failed to save uploaded file in process endpoint: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save direct upload file."
            )
    elif session_id:
        # Load from previously uploaded session
        # Find file in temporary uploads matching session_id prefix
        matching_files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(session_id)]
        if not matching_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prescription image for the provided session_id was not found. Please upload again."
            )
        image_name = matching_files[0]
        filepath = os.path.join(UPLOAD_DIR, image_name)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either session_id or file must be provided."
        )

    # Ensure clean file removal after request finishes processing
    background_tasks.add_task(cleanup_file, filepath)

    # 2. Run OCR Pipeline
    logger.info(f"Processing prescription image for session {resolved_session_id}")
    start_time = time.time()

    try:
        # Load image via OpenCV
        img_bgr = cv2.imread(filepath)
        if img_bgr is None:
            raise ValueError("Failed to load image matrix from temporary file path.")

        # -- PHASE 1: DOCUMENT DETECTION & PERSPECTIVE WARP --
        detection = scanner_service.detect_document(img_bgr)
        if detection["detected"]:
            # Crop and apply perspective transformation
            warped = scanner_service.correct_perspective(img_bgr, detection["points"])
        else:
            # Fallback to whole image if no boundary detected
            warped = img_bgr

        # -- PHASE 2: IMAGE ENHANCEMENT --
        enhanced = scanner_service.enhance_document(warped)

        # -- PHASE 3: OCR EXTRACTION --
        ocr_result = ocr_service.extract_text(enhanced)
        raw_text = ocr_result["text"]
        confidence = ocr_result["confidence"]

        # -- PHASE 4: PRESCRIPTION PARSER --
        structured_data = parser_service.parse(raw_text)

        # -- PHASE 5: MEDICATION SAFETY CHECK --
        warnings = safety_service.check_safety(structured_data, confidence)

        # -- DATABASE STORAGE --
        record_id = str(uuid.uuid4())
        saved = save_prescription(
            db_path=DB_PATH,
            prescription_id=record_id,
            session_id=resolved_session_id,
            uploaded_by=uploaded_by,
            image_name=image_name,
            raw_text=raw_text,
            structured_data=structured_data,
            confidence=confidence
        )

        duration = time.time() - start_time
        logger.info(f"Processing complete for session {resolved_session_id} in {duration:.2f}s. Saved to DB: {saved}")

        return {
            "success": True,
            "id": record_id,
            "session_id": resolved_session_id,
            "raw_text": raw_text,
            "structured_data": structured_data,
            "warnings": warnings,
            "confidence": confidence
        }

    except Exception as e:
        logger.error(f"Error processing prescription workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during prescription processing: {str(e)}"
        )

@router.get("/api/v1/prescription/{id}")
async def get_prescription_by_id(
    request: Request,
    id: str
):
    """Retrieves prescription processing results by unique DB ID."""
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check_rate_limit(client_ip)

    logger.info(f"Retrieving prescription record for ID {id} from IP {client_ip}")
    record = get_prescription(DB_PATH, id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescription record with ID '{id}' was not found."
        )
    return {
        "success": True,
        "data": record
    }

app = FastAPI(
    title="MediSign AI Prescription OCR Service",
    description="Microservice providing document boundary detection, enhancement, OCR text extraction, parsing, and drug safety verification.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("OCR_PORT", "5002"))
    logger.info(f"Launching OCR Service on port {port}...")
    uvicorn.run("ocr_service:app", host="0.0.0.0", port=port, reload=True)
