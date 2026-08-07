from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.avatar_router import router as avatar_router
from routers.emergency_router import router as emergency_router
from routers.prescription_router import router as prescription_router
from routers.sign_router import router as sign_router
from routers.speech_router import router as speech_router
from routers.triage_router import router as triage_router

app = FastAPI(title="MediSign AI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sign_router)
app.include_router(avatar_router)
app.include_router(emergency_router)
app.include_router(speech_router)
app.include_router(prescription_router)
app.include_router(triage_router)



@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)

