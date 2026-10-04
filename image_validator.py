from PIL import Image
import os


def validate_image(image_path, image_type="Image"):
    result = {
        "valid": False,
        "message": "",
        "width": 0,
        "height": 0,
        "format": "",
        "mode": ""
    }

    if not os.path.exists(image_path):
        result["message"] = f"{image_type} file not found."
        return result

    try:
        with Image.open(image_path) as image:
            image.verify()

        with Image.open(image_path) as image:
            width, height = image.size
            image_format = image.format
            mode = image.mode

        result["width"] = width
        result["height"] = height
        result["format"] = image_format
        result["mode"] = mode

        if width < 100 or height < 100:
            result["message"] = (
                f"{image_type} image is too small. "
                "Minimum recommended size is 100x100."
            )
            return result

        result["valid"] = True
        result["message"] = f"{image_type} image is valid."

    except Exception as e:
        result["message"] = (
            f"{image_type} image is invalid or corrupted: {e}"
        )

    return result


if __name__ == "__main__":

    print("=" * 60)
    print("AI VIRTUAL FASHION STUDIO")
    print("IMAGE VALIDATION MODULE")
    print("=" * 60)

    person_path = "outputs/person_processed.png"
    garment_path = "outputs/garment_processed.png"

    person_result = validate_image(person_path, "Person")
    garment_result = validate_image(garment_path, "Garment")

    print("\nPERSON IMAGE")
    print("-" * 40)
    for key, value in person_result.items():
        print(f"{key}: {value}")

    print("\nGARMENT IMAGE")
    print("-" * 40)
    for key, value in garment_result.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 60)
    print("Image validation completed.")
    print("=" * 60)
