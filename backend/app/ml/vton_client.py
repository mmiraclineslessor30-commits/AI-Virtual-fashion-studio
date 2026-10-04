
from pathlib import Path
from typing import Dict, Any
import shutil
import uuid

from gradio_client import Client, handle_file


BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class VTONClient:

    def __init__(self):
        self.client = Client("yisol/IDM-VTON")

    def predict(
        self,
        person_path: Path,
        garment_path: Path,
    ) -> Dict[str, Any]:

        if not person_path.exists():
            raise FileNotFoundError(
                f"Person image not found: {person_path}"
            )

        if not garment_path.exists():
            raise FileNotFoundError(
                f"Garment image not found: {garment_path}"
            )

        result = self.client.predict(
            {
                "background": handle_file(str(person_path)),
                "layers": [],
                "composite": None,
            },
            handle_file(str(garment_path)),
            "clothing",
            True,
            False,
            30,
            42,
            api_name="/tryon",
        )

        output_path = Path(result[0])
        masked_output_path = Path(result[1])

        if not output_path.exists():
            raise FileNotFoundError(
                "IDM-VTON did not return a generated image."
            )

        output_name = f"tryon_{uuid.uuid4().hex}.png"
        saved_output = OUTPUT_DIR / output_name
        shutil.copy2(output_path, saved_output)

        saved_masked = None
        if masked_output_path.exists():
            masked_name = f"masked_{uuid.uuid4().hex}.png"
            saved_masked = OUTPUT_DIR / masked_name
            shutil.copy2(masked_output_path, saved_masked)

        return {
            "status": "completed",
            "model": "IDM-VTON",
            "provider": "Hugging Face Space",
            "output": str(saved_output),
            "output_filename": output_name,
            "masked_output": (
                str(saved_masked) if saved_masked else None
            ),
        }