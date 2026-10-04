
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ml.pipeline import FashionPipeline


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title="AURA Studio API",
    version="1.0.0",
)

# Serve generated try-on images
app.mount(
    "/outputs",
    StaticFiles(directory=str(OUTPUT_DIR)),
    name="outputs",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5177",
        "http://127.0.0.1:5177",
        "http://localhost:5178",
        "http://127.0.0.1:5178",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


pipeline = FashionPipeline()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "ml_engine": "AURA Fashion Intelligence Pipeline",
        "model": getattr(
            pipeline,
            "name",
            "AURA-VTON",
        ),
    }


@app.post("/analyze")
async def analyze(
    person: UploadFile = File(...),
    garment: UploadFile = File(...),
):
    # Save uploaded images
    person_filename = Path(person.filename or "person.png").name
    garment_filename = Path(garment.filename or "garment.png").name

    person_path = UPLOAD_DIR / f"person_{person_filename}"
    garment_path = UPLOAD_DIR / f"garment_{garment_filename}"

    person_data = await person.read()
    garment_data = await garment.read()

    person_path.write_bytes(person_data)
    garment_path.write_bytes(garment_data)

    # Run virtual try-on pipeline
    result = pipeline.run(
        person_path=person_path,
        garment_path=garment_path,
    )

    # Return a browser-accessible URL for generated images
    inference = result.get("inference", {})
    inference_result = inference.get("result", {})

    output_filename = inference_result.get("output_filename")
    if output_filename:
        inference_result["output_url"] = (
            f"/outputs/{Path(output_filename).name}"
        )

    masked_filename = inference_result.get("masked_output")
    if masked_filename:
        masked_path = Path(masked_filename)
        if masked_path.exists():
            inference_result["masked_output_url"] = (
                f"/outputs/{masked_path.name}"
            )

    return {
        "success": True,
        "message": "Virtual try-on completed successfully.",
        "person_filename": person_filename,
        "garment_filename": garment_filename,
        "pipeline": result,
    }