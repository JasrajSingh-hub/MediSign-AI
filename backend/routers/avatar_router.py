from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.avatar_service import parse_avatar_text

router = APIRouter(prefix="/api/v1/avatar", tags=["avatar"])


class TextPayLoad(BaseModel):
    text: str


@router.post("/parse")
async def avatar_parse(payload: TextPayLoad):
    try:
        raw_text = payload.text.strip()
        if not raw_text:
            raise HTTPException(status_code=400, detail="No text content provided")
        return parse_avatar_text(raw_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(exc)})
