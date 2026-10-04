from PIL import Image
import os

INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def preprocess_image(input_path, output_name):
    image = Image.open(input_path).convert("RGB")
    image = image.resize((768, 1024))

    output_path = os.path.join(OUTPUT_DIR, output_name)
    image.save(output_path)

    print(f"Processed image saved: {output_path}")


if __name__ == "__main__":
    print("AI Virtual Fashion Studio - Image Preprocessing")

    person_path = os.path.join(INPUT_DIR, "person.jpg")
    garment_path = os.path.join(INPUT_DIR, "garment.jpg")

    if os.path.exists(person_path):
        preprocess_image(person_path, "person_processed.png")
    else:
        print("Person image not found:", person_path)

    if os.path.exists(garment_path):
        preprocess_image(garment_path, "garment_processed.png")
    else:
        print("Garment image not found:", garment_path)