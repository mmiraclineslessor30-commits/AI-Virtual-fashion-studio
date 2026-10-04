from gradio_client import Client, handle_file
from pathlib import Path


SPACE_ID = "yisol/IDM-VTON"


def _get_path(value):
    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        return value.get("path") or value.get("url")

    return None


def run_virtual_tryon(
    person_path,
    garment_path,
    garment_description="short sleeve t-shirt",
    auto_mask=True,
    auto_crop=False,
    denoise_steps=30,
    seed=42
):
    person_path = str(Path(person_path))
    garment_path = str(Path(garment_path))

    if not Path(person_path).exists():
        raise FileNotFoundError(f"Person image not found: {person_path}")

    if not Path(garment_path).exists():
        raise FileNotFoundError(f"Garment image not found: {garment_path}")

    print("Connecting to official IDM-VTON Space...")

    client = Client(SPACE_ID)

    human_image = {
        "background": handle_file(person_path),
        "layers": [],
        "composite": None
    }

    print("Submitting virtual try-on request...")
    print("Garment description:", garment_description)

    result = client.predict(
        human_image,
        handle_file(garment_path),
        garment_description,
        auto_mask,
        auto_crop,
        denoise_steps,
        seed,
        api_name="/tryon"
    )

    output_value = result[0]
    mask_value = result[1] if len(result) > 1 else None

    output_path = _get_path(output_value)
    mask_path = _get_path(mask_value)

    if not output_path:
        raise RuntimeError(
            f"IDM-VTON returned an unexpected output: {result}"
        )

    return output_path, mask_path


if __name__ == "__main__":

    person = "outputs/person_processed.png"
    garment = "outputs/garment_processed.png"

    try:
        output, mask = run_virtual_tryon(
            person,
            garment,
            garment_description="short sleeve t-shirt",
            auto_mask=True,
            auto_crop=False,
            denoise_steps=30,
            seed=42
        )

        print("\n" + "=" * 60)
        print("IDM-VTON RESULT")
        print("=" * 60)

        print("Output:", output)

        if mask:
            print("Mask:", mask)

        print("=" * 60)

    except Exception as e:
        print("\nIDM-VTON ERROR")
        print("-" * 60)
        print(e)
