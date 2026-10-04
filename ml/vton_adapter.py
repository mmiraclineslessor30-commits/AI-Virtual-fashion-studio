from pathlib import Path
from typing import Dict


class VTONAdapter:

    def __init__(self):
        self.name = "AURA-VTON Adapter"
        self.ready = False

    def check_inputs(
        self,
        person_path: Path,
        garment_path: Path,
    ) -> Dict:

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
    ) -> Dict:

        inputs = self.check_inputs(
            person_path,
            garment_path,
        )

        return {
            "status": "adapter_ready",
            "adapter": self.name,
            "model_loaded": False,
            "inputs": inputs,
            "message": (
                "VTON model adapter is ready "
                "for model integration."
            ),
        }