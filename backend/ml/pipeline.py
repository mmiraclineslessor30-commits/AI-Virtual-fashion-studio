from pathlib import Path

from ml.inference import VirtualTryOnEngine


class FashionPipeline:

    def __init__(self):
        self.name = "AURA Fashion Intelligence Pipeline"
        self.model_name = "AURA-VTON"
        self.engine = VirtualTryOnEngine()

    def validate_inputs(
        self,
        person_path: Path,
        garment_path: Path,
    ) -> bool:

        if not person_path.exists():
            raise FileNotFoundError(
                f"Person image not found: {person_path}"
            )

        if not garment_path.exists():
            raise FileNotFoundError(
                f"Garment image not found: {garment_path}"
            )

        return True

    def run(
        self,
        person_path: Path,
        garment_path: Path,
    ):

        self.validate_inputs(
            person_path,
            garment_path,
        )

        inference_result = self.engine.predict(
            person_path=person_path,
            garment_path=garment_path,
        )

        return {
            "status": "pipeline_ready",
            "model": self.model_name,
            "device": self.engine.device,
            "inference": inference_result,
        }