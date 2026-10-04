from PIL import Image
import os

INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def find_image(prefix):
    """Find an image whose filename starts with the given prefix."""
    supported_extensions = [".jpg", ".jpeg", ".png", ".webp"]

    for filename in os.listdir(INPUT_DIR):
        name, ext = os.path.splitext(filename)

        if name.lower() == prefix.lower() and ext.lower() in supported_extensions:
            return os.path.join(INPUT_DIR, filename)

    return None


def preprocess_image(input_path, output_name):
    try:
        image = Image.open(input_path).convert("RGB")

        print(f"Original size: {image.size}")

        image = image.resize((768, 1024))

        output_path = os.path.join(OUTPUT_DIR, output_name)
        image.save(output_path)

        print(f"Processed image saved: {output_path}")

    except Exception as e:
        print(f"Error processing {input_path}: {e}")


if __name__ == "__main__":

    print("=" * 50)
    print("AI Virtual Fashion Studio")
    print("Image Preprocessing")
    print("=" * 50)

    person_path = find_image("person")
    garment_path = find_image("garment")

    # Person image
    if person_path:
        print(f"\nPerson image found: {person_path}")
        preprocess_image(
            person_path,
            "person_processed.png"
        )
    else:
        print("\nPerson image not found!")
        print("Please put your image inside the 'inputs' folder")
        print("and name it person.jpg / person.png / person.jpeg / person.webp")

    # Garment image
    if garment_path:
        print(f"\nGarment image found: {garment_path}")
        preprocess_image(
            garment_path,
            "garment_processed.png"
        )
    else:
        print("\nGarment image not found!")
        print("Please put your garment image inside the 'inputs' folder")
        print("and name it garment.jpg / garment.png / garment.jpeg / garment.webp")

    print("\n" + "=" * 50)
    print("Preprocessing completed.")
    print("=" * 50)