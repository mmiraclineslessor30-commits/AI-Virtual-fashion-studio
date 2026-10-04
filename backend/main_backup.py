from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ml.pipeline import FashionPipeline


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True)


app = FastAPI(
    title="AURA Studio API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


fashion_pipeline = FashionPipeline()


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "AURA Studio API",
        "version": "1.0.0",
        "ml_engine": fashion_pipeline.name,
        "model": fashion_pipeline.model_name,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "ml_engine": fashion_pipeline.name,
        "model": fashion_pipeline.model_name,
    }


@app.post("/analyze")
async def analyze(
    person: UploadFile = File(...),
    garment: UploadFile = File(...),
):
    person_data = await person.read()
    garment_data = await garment.read()

    person_path = (
        UPLOAD_DIR / f"person_{person.filename}"
    )

    garment_path = (
        UPLOAD_DIR / f"garment_{garment.filename}"
    )

    person_path.write_bytes(person_data)
    garment_path.write_bytes(garment_data)

    pipeline_result = fashion_pipeline.run(
        person_path=person_path,
        garment_path=garment_path,
    )

    return {
        "success": True,
        "message": "Images received and ML pipeline initialized.",
        "person_filename": person.filename,
        "garment_filename": garment.filename,
        "pipeline": pipeline_result,
    }