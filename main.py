from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from ml.pipeline import FashionPipeline


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="AURA Studio API",
    version="1.0.0",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5177",
        "http://127.0.0.1:5177",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# ML Pipeline
# --------------------------------------------------

pipeline = FashionPipeline()


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "ml_engine": "AURA Fashion Intelligence Pipeline",
        "model": getattr(pipeline, "name", "AURA-VTON"),
    }


# --------------------------------------------------
# Analyze / Virtual Try-On
# --------------------------------------------------

@app.post("/analyze")
async def analyze(
    person: UploadFile = File(...),
    garment: UploadFile = File(...),
):
    person_data = await person.read()
    garment_data = await garment.read()

    person_path = UPLOAD_DIR / f"person_{person.filename}"
    garment_path = UPLOAD_DIR / f"garment_{garment.filename}"

    person_path.write_bytes(person_data)
    garment_path.write_bytes(garment_data)

    return {
        "success": True,
        "message": "Images received and ML pipeline initialized.",
        "person_filename": person.filename,
        "garment_filename": garment.filename,
        "pipeline": {
            "status": "pipeline_ready",
            "model": getattr(pipeline, "name", "AURA-VTON"),
            "device": "cpu",
            "inference": {
                "status": "ready_for_inference",
                "engine": "AURA-VTON",
                "device": "cpu",
                "model_loaded": False,
                "inputs": {
                    "person": str(person_path),
                    "garment": str(garment_path),
                },
            },
        },
    }