from pathlib import Path

from PIL import Image

from ml.config import get_model_config
from ml.vton_adapter import VTONAdapter


class VirtualTryOnEngine:

    def __init__(self):
        self.config = get_model_config()

        self.device = self.config.device
        self.model_name = self.config.name
        self.model_loaded = self.config.model_loaded

        self.adapter = VTONAdapter()

    def validate_image(self, image_path: Path):

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        with Image.open(image_path) as image:
            image.verify()

        return True

    def prepare_inputs(
        self,
        person_path: Path,
        garment_path: Path,
    ):

        self.validate_image(person_path)
        self.validate_image(garment_path)

        return {
            "person": str(person_path),
            "garment": str(garment_path),
        }

    def predict(
        self,
        person_path: Path,
        garment_path: Path,
    ):

        inputs = self.prepare_inputs(
            person_path,
            garment_path,
        )

        adapter_result = self.adapter.run(
            person_path=person_path,
            garment_path=garment_path,
        )

        return {
            "status": "ready_for_model",
            "engine": self.model_name,
            "device": self.device,
            "model_loaded": self.model_loaded,
            "inputs": inputs,
            "adapter": adapter_result,
        }