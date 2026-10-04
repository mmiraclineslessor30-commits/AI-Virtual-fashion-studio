from PIL import Image, ImageStat
import os

INPUT_IMAGE = "outputs/garment_processed.png"


def classify_brightness(value):
    if value < 70:
        return "Dark"
    elif value < 150:
        return "Medium"
    else:
        return "Light"


def classify_texture(image):
    gray = image.convert("L")
    stat = ImageStat.Stat(gray)
    variation = stat.stddev[0]

    if variation < 25:
        return "Low"
    elif variation < 55:
        return "Medium"
    else:
        return "High"


def get_dominant_color(image):
    small_image = image.resize((100, 100))
    quantized = small_image.quantize(colors=8)

    palette = quantized.getpalette()
    color_counts = quantized.getcolors()

    if not color_counts:
        return (0, 0, 0)

    dominant_index = max(color_counts)[1]

    r = palette[dominant_index * 3]
    g = palette[dominant_index * 3 + 1]
    b = palette[dominant_index * 3 + 2]

    return (r, g, b)


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def analyze_garment(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Garment image not found: {image_path}"
        )

    image = Image.open(image_path).convert("RGB")

    width, height = image.size
    stat = ImageStat.Stat(image)

    mean_r, mean_g, mean_b = stat.mean
    brightness = (mean_r + mean_g + mean_b) / 3

    dominant_rgb = get_dominant_color(image)
    dominant_hex = rgb_to_hex(dominant_rgb)

    aspect_ratio = width / height
    texture = classify_texture(image)
    brightness_category = classify_brightness(brightness)

    if aspect_ratio < 0.65:
        shape = "Portrait-oriented garment image"
    elif aspect_ratio > 1.35:
        shape = "Landscape-oriented garment image"
    else:
        shape = "Balanced garment image"

    return {
        "Image Width": width,
        "Image Height": height,
        "Aspect Ratio": round(aspect_ratio, 2),
        "Brightness": round(brightness, 2),
        "Brightness Category": brightness_category,
        "Dominant RGB": dominant_rgb,
        "Dominant Color": dominant_hex,
        "Texture Level": texture,
        "Image Shape": shape
    }


if __name__ == "__main__":

    print("=" * 60)
    print("AI VIRTUAL FASHION STUDIO")
    print("GARMENT INTELLIGENCE MODULE")
    print("=" * 60)

    try:
        result = analyze_garment(INPUT_IMAGE)

        print("\nGarment Analysis Result")
        print("-" * 40)

        for key, value in result.items():
            print(f"{key}: {value}")

        print("\n" + "=" * 60)
        print("Garment analysis completed successfully.")
        print("=" * 60)

    except Exception as e:
        print("\nERROR")
        print("-" * 40)
        print(e)
