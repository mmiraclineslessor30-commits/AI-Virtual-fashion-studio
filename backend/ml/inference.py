from pathlib import Path

from ml.vton_adapter import VTONAdapter


class VirtualTryOnEngine:
    """
    Virtual try-on inference engine.

    The engine validates inputs and delegates IDM-VTON execution
    to the VTON adapter. Local CPU environments report that GPU
    inference is required rather than attempting to load the model.
    """

    def __init__(self):
        self.adapter = VTONAdapter()
        self.device = self.adapter.device
        self.model_loaded = False
        self.model_name = self.adapter.backend

    def validate_image(self, image_path: Path):
        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        return True

    def prepare_inputs(
        self,
        person_path: Path,
        garment_path: Path,
    ):
        self.validate_image(person_path)
        self.validate_image(garment_path)

        return self.adapter.check_inputs(
            person_path,
            garment_path,
        )

    def predict(
        self,
        person_path: Path,
        garment_path: Path,
    ):
        self.prepare_inputs(
            person_path,
            garment_path,
        )

        return self.adapter.run(
            person_path,
            garment_path,
        )
