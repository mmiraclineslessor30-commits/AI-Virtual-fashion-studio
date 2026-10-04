from pathlib import Path

import torch
from fastapi import FastAPI, UploadFile, File


BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "inputs"
OUTPUT_DIR = BASE_DIR / "outputs"

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


app = FastAPI(
    title="AURA VTON GPU Service",
    version="1.0.0",
)


@app.get("/health")
async def health():
    cuda_available = torch.cuda.is_available()

    return {
        "status": "healthy",
        "service": "AURA VTON GPU Service",
        "backend": "IDM-VTON",
        "model_loaded": False,
        "cuda_available": cuda_available,
        "gpu": (
            torch.cuda.get_device_name(0)
            if cuda_available
            else None
        ),
    }


@app.post("/v1/tryon")
async def tryon(
    person: UploadFile = File(...),
    garment: UploadFile = File(...),
):
    person_path = INPUT_DIR / f"person_{person.filename}"
    garment_path = INPUT_DIR / f"garment_{garment.filename}"

    person_path.write_bytes(await person.read())
    garment_path.write_bytes(await garment.read())

    return {
        "status": "gpu_inference_pending",
        "backend": "IDM-VTON",
        "model_loaded": False,
        "cuda_available": torch.cuda.is_available(),
        "person": str(person_path),
        "garment": str(garment_path),
        "message": (
            "GPU service is reachable. "
            "IDM-VTON inference will be executed here."
        ),
    }
