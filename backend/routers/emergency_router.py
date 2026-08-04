from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from services.emergency_service import health, predict, status

router = APIRouter(prefix="/api/v1/emergency", tags=["emergency"])


class ImagePayload(BaseModel):
    image: str


@router.get("/health")
def emergency_health():
    return health()


@router.get("/status")
def emergency_status():
    return status()


@router.post("/predict")
def emergency_predict(
    file: UploadFile | None = File(None),
    image_base64: str | None = Form(None),
) -> dict:
    if file is not None:
        return predict(file_bytes=file.file.read())
    if image_base64:
        return predict(image_base64=image_base64)
    raise HTTPException(status_code=400, detail="Provide an image via file upload or image_base64.")
