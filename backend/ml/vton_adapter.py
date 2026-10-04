from pathlib import Path
from typing import Dict, Any
import os

from app.ml.vton_client import VTONClient


class VTONAdapter:

    def __init__(self):
        self.name = "AURA-VTON Adapter"
        self.backend = "IDM-VTON"
        self.device = "cpu"
        self.ready = False

        self.remote_enabled = os.getenv(
            "VTON_REMOTE_ENABLED",
            "false",
        ).lower() == "true"

        self.client = (
            VTONClient()
            if self.remote_enabled
            else None
        )

    def check_inputs(
        self,
        person_path: Path,
        garment_path: Path,
    ) -> Dict[str, str]:

        if not person_path.exists():
            raise FileNotFoundError(
                f"Person image not found: {person_path}"
            )

        if not garment_path.exists():
            raise FileNotFoundError(
                f"Garment image not found: {garment_path}"
            )

        return {
            "person": str(person_path),
            "garment": str(garment_path),
        }

    def run(
        self,
        person_path: Path,
        garment_path: Path,
    ) -> Dict[str, Any]:

        inputs = self.check_inputs(
            person_path,
            garment_path,
        )

        if self.remote_enabled and self.client:
            result = self.client.predict(
                person_path,
                garment_path,
            )

            return {
                "status": "completed",
                "adapter": self.name,
                "backend": self.backend,
                "device": "remote_gpu",
                "model_loaded": True,
                "inputs": inputs,
                "result": result,
            }

        return {
            "status": "gpu_required",
            "adapter": self.name,
            "backend": self.backend,
            "device": self.device,
            "model_loaded": False,
            "inputs": inputs,
            "message": (
                "IDM-VTON local inference requires "
                "a compatible GPU environment. "
                "Set VTON_REMOTE_ENABLED=true to use "
                "the remote GPU inference service."
            ),
        }
