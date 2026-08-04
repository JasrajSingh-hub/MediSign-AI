from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.sign_service import predict_sign

router = APIRouter(tags=["sign"])


class ImagePayLoad(BaseModel):
    image: str


@router.post("/predict")
async def sign_predict(payload: ImagePayLoad):
    try:
        return predict_sign(payload.image)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
