from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import ensure_database_ready
from app.modules.prescription.router import router as prescription_router

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

app = FastAPI(title="MediSign AI - Module B API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(prescription_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def startup_event():
    ensure_database_ready()
