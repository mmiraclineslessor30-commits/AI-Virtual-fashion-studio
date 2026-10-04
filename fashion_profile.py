from pathlib import Path
import math
import urllib.parse

from PIL import Image
import numpy as np
import cv2


# ---------------------------------------------------------
# COLOR PALETTES
# ---------------------------------------------------------

PALETTES = {
    "Warm": {
        "best": [
            "Cream",
            "Olive",
            "Rust",
            "Terracotta",
            "Mustard",
            "Chocolate",
            "Coral",
        ],
        "rgb": [
            (245, 238, 220),
            (108, 120, 60),
            (183, 75, 45),
            (190, 95, 60),
            (210, 165, 55),
            (92, 55, 35),
            (235, 105, 85),
        ],
    },
    "Cool": {
        "best": [
            "Navy",
            "Plum",
            "Emerald",
            "Cobalt",
            "Berry",
            "Icy Blue",
            "Lavender",
        ],
        "rgb": [
            (25, 45, 90),
            (95, 50, 110),
            (35, 120, 80),
            (35, 80, 180),
            (150, 45, 85),
            (170, 215, 240),
            (175, 150, 210),
        ],
    },
    "Neutral": {
        "best": [
            "Teal",
            "Rose",
            "Navy",
            "Cream",
            "Forest Green",
            "Dusty Blue",
            "Mauve",
        ],
        "rgb": [
            (35, 125, 125),
            (190, 100, 110),
            (25, 45, 90),
            (245, 238, 220),
            (40, 95, 65),
            (100, 145, 175),
            (155, 105, 125),
        ],
    },
}


# ---------------------------------------------------------
# VISIBLE SKIN-TONE ESTIMATION
# ---------------------------------------------------------

def estimate_skin_tone(image_path):
    """
    Estimates visible skin-tone depth and undertone from
    a person image for clothing color coordination.

    This is a computer-vision heuristic, not an identity
    or race classifier.
    """

    try:
        image = cv2.imread(str(image_path))

        if image is None:
            return {
                "Tone": "Unknown",
                "Undertone": "Unknown",
                "Confidence": 0,
                "Method": "Image could not be read"
            }

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        cascade_path = cv2.data.haarcascades + (
            "haarcascade_frontalface_default.xml"
        )

        face_detector = cv2.CascadeClassifier(cascade_path)

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40)
        )

        pixels = None

        if len(faces) > 0:

            # Largest detected face
            x, y, w, h = max(
                faces,
                key=lambda f: f[2] * f[3]
            )

            face = image_rgb[
                y + int(h * 0.25): y + int(h * 0.75),
                x + int(w * 0.20): x + int(w * 0.80)
            ]

            pixels = face.reshape(-1, 3)

        else:

            # Fallback to upper-center region
            height, width = image_rgb.shape[:2]

            crop = image_rgb[
                0:int(height * 0.45),
                int(width * 0.25):int(width * 0.75)
            ]

            pixels = crop.reshape(-1, 3)

        if pixels is None or len(pixels) == 0:
            raise ValueError("No usable skin region found.")

        # Keep pixels in a broad skin-like RGB range.
        r = pixels[:, 0]
        g = pixels[:, 1]
        b = pixels[:, 2]

        mask = (
            (r > 60) &
            (g > 35) &
            (b > 20) &
            (r > g * 0.85) &
            (g > b * 0.75) &
            ((r - b) > 15)
        )

        skin_pixels = pixels[mask]

        if len(skin_pixels) < 30:
            return {
                "Tone": "Unknown",
                "Undertone": "Unknown",
                "Confidence": 25,
                "Method": "Insufficient visible skin pixels"
            }

        mean_rgb = skin_pixels.mean(axis=0)

        r_mean = float(mean_rgb[0])
        g_mean = float(mean_rgb[1])
        b_mean = float(mean_rgb[2])

        luminance = (
            0.2126 * r_mean +
            0.7152 * g_mean +
            0.0722 * b_mean
        )

        if luminance >= 190:
            tone = "Light"
        elif luminance >= 150:
            tone = "Medium"
        elif luminance >= 110:
            tone = "Tan"
        else:
            tone = "Deep"

        red_blue = r_mean - b_mean
        green_blue = g_mean - b_mean

        if red_blue > 35 and green_blue > 10:
            undertone = "Warm"
        elif b_mean - r_mean > 15:
            undertone = "Cool"
        else:
            undertone = "Neutral"

        # Confidence is intentionally conservative.
        pixel_confidence = min(
            95,
            50 + int(len(skin_pixels) / 500)
        )

        return {
            "Tone": tone,
            "Undertone": undertone,
            "Confidence": pixel_confidence,
            "Method": "Computer-vision visible-tone estimate"
        }

    except Exception as exc:

        return {
            "Tone": "Unknown",
            "Undertone": "Unknown",
            "Confidence": 0,
            "Method": str(exc)
        }


# ---------------------------------------------------------
# BODY SILHOUETTE PROFILE
# ---------------------------------------------------------

def estimate_body_profile(
    bust,
    waist,
    hip
):
    """
    Measurement-based silhouette classification.

    Uses user-provided measurements instead of guessing
    measurements from an image.
    """

    bust = float(bust)
    waist = float(waist)
    hip = float(hip)

    upper_average = (bust + hip) / 2

    waist_ratio = waist / upper_average

    if waist_ratio >= 0.92:
        silhouette = "Midsection-dominant"

    elif hip >= bust * 1.08:
        silhouette = "Lower-body dominant"

    elif bust >= hip * 1.08:
        silhouette = "Upper-body dominant"

    elif waist_ratio <= 0.80:
        silhouette = "Balanced-defined"

    else:
        silhouette = "Straight-balanced"

    return {
        "Silhouette Profile": silhouette,
        "Bust": round(bust, 1),
        "Waist": round(waist, 1),
        "Hip": round(hip, 1),
        "Waist Ratio": round(waist_ratio, 2)
    }


# ---------------------------------------------------------
# GARMENT CATEGORY
# ---------------------------------------------------------

def detect_garment_category(description):

    text = description.lower()

    categories = {
        "dress": [
            "dress",
            "gown",
            "frock"
        ],
        "top": [
            "t-shirt",
            "tshirt",
            "shirt",
            "top",
            "blouse",
            "kurti",
            "tunic"
        ],
        "outerwear": [
            "blazer",
            "jacket",
            "coat",
            "cardigan"
        ],
        "bottom": [
            "jeans",
            "trouser",
            "pants",
            "skirt",
            "shorts"
        ],
        "traditional": [
            "saree",
            "sari",
            "lehenga",
            "salwar",
            "kurta",
            "ethnic"
        ]
    }

    for category, keywords in categories.items():

        for keyword in keywords:

            if keyword in text:
                return category

    return "general"


# ---------------------------------------------------------
# SILHOUETTE SCORE
# ---------------------------------------------------------

def silhouette_score(
    body_profile,
    garment_category
):

    profile = body_profile["Silhouette Profile"]

    score = 75

    reasons = []

    rules = {

        "Lower-body dominant": {
            "top": 88,
            "dress": 84,
            "outerwear": 86,
            "traditional": 85,
            "general": 78
        },

        "Upper-body dominant": {
            "top": 76,
            "dress": 84,
            "outerwear": 74,
            "traditional": 82,
            "general": 78
        },

        "Midsection-dominant": {
            "top": 82,
            "dress": 84,
            "outerwear": 88,
            "traditional": 82,
            "general": 80
        },

        "Balanced-defined": {
            "top": 88,
            "dress": 90,
            "outerwear": 84,
            "traditional": 88,
            "general": 85
        },

        "Straight-balanced": {
            "top": 84,
            "dress": 82,
            "outerwear": 86,
            "traditional": 83,
            "general": 82
        }
    }

    score = rules.get(
        profile,
        {}
    ).get(
        garment_category,
        75
    )

    if profile == "Lower-body dominant":
        reasons.append(
            "Structured or visually interesting upper garments "
            "can create a balanced overall silhouette."
        )

    elif profile == "Upper-body dominant":
        reasons.append(
            "Cleaner shoulder detailing and balanced lower "
            "visual weight can create a proportionate look."
        )

    elif profile == "Midsection-dominant":
        reasons.append(
            "Layering and controlled drape can create longer "
            "vertical visual lines."
        )

    elif profile == "Balanced-defined":
        reasons.append(
            "The silhouette supports both structured and "
            "waist-defining styling approaches."
        )

    else:
        reasons.append(
            "Layering, texture and proportion changes can add "
            "visual structure to the outfit."
        )

    return score, reasons


# ---------------------------------------------------------
# COLOR DISTANCE
# ---------------------------------------------------------

def color_distance(rgb1, rgb2):

    return math.sqrt(
        sum(
            (float(a) - float(b)) ** 2
            for a, b in zip(rgb1, rgb2)
        )
    )


def color_harmony_score(
    garment_rgb,
    undertone
):

    palette = PALETTES.get(
        undertone,
        PALETTES["Neutral"]
    )

    distances = [
        color_distance(
            garment_rgb,
            palette_rgb
        )
        for palette_rgb in palette["rgb"]
    ]

    nearest = min(distances)

    # Converts color distance into a readable heuristic score.
    score = 100 - min(
        75,
        nearest / 255 * 75
    )

    return round(score), palette["best"]


# ---------------------------------------------------------
# OCCASION SCORE
# ---------------------------------------------------------

def occasion_score(
    description,
    occasion
):

    text = description.lower()
    occasion_text = occasion.lower()

    score = 68
    reason = (
        "The garment can be styled for the selected occasion "
        "with suitable accessories."
    )

    if occasion_text == "college / casual":

        if any(
            word in text
            for word in [
                "t-shirt",
                "tshirt",
                "shirt",
                "jeans",
                "casual"
            ]
        ):
            score = 92
            reason = (
                "The garment description fits a relaxed "
                "college/casual setting."
            )

    elif occasion_text == "office / formal":

        if any(
            word in text
            for word in [
                "blazer",
                "formal",
                "shirt",
                "trouser",
                "dress"
            ]
        ):
            score = 92
            reason = (
                "The garment can fit a polished professional "
                "setting with structured accessories."
            )

    elif occasion_text == "party / evening":

        if any(
            word in text
            for word in [
                "dress",
                "gown",
                "party",
                "sequin",
                "blazer"
            ]
        ):
            score = 94
            reason = (
                "The garment description supports an evening "
                "or party styling context."
            )

    elif occasion_text == "traditional / festive":

        if any(
            word in text
            for word in [
                "saree",
                "sari",
                "lehenga",
                "kurta",
                "ethnic",
                "salwar"
            ]
        ):
            score = 95
            reason = (
                "The garment description aligns closely with "
                "traditional or festive styling."
            )

    return score, reason


# ---------------------------------------------------------
# ACCESSORY RECOMMENDATIONS
# ---------------------------------------------------------

def accessory_recommendations(
    occasion,
    garment_category,
    undertone
):

    if occasion == "Office / Formal":

        accessories = [
            (
                "Minimalist watch",
                "A clean watch keeps the formal outfit polished."
            ),
            (
                "Structured handbag",
                "Adds a professional silhouette."
            ),
            (
                "Block heels or loafers",
                "Balances comfort and formal styling."
            )
        ]

    elif occasion == "Party / Evening":

        accessories = [
            (
                "Statement earrings",
                "Adds visual focus around the face."
            ),
            (
                "Clutch bag",
                "Works well with evening styling."
            ),
            (
                "Block or heeled sandals",
                "Completes the party look."
            )
        ]

    elif occasion == "Traditional / Festive":

        accessories = [
            (
                "Jhumka earrings",
                "Complements traditional styling."
            ),
            (
                "Embroidered potli bag",
                "Adds a festive accessory element."
            ),
            (
                "Ethnic footwear",
                "Completes the traditional outfit."
            )
        ]

    else:

        accessories = [
            (
                "Hoop or stud earrings",
                "Simple accessory for an everyday look."
            ),
            (
                "Crossbody or tote bag",
                "Practical for college and casual use."
            ),
            (
                "Clean sneakers",
                "Keeps the outfit comfortable and contemporary."
            )
        ]

    # Generate shopping/search links instead of pretending these
    # are guaranteed product matches.
    result = []

    for name, reason in accessories:

        query = urllib.parse.quote(
            name
        )

        amazon = (
            f"https://www.amazon.in/s?k={query}"
        )

        myntra = (
            f"https://www.myntra.com/search?q={query}"
        )

        result.append({
            "Accessory": name,
            "Why": reason,
            "Amazon Search": amazon,
            "Myntra Search": myntra
        })

    return result


# ---------------------------------------------------------
# FULL FASHION PROFILE
# ---------------------------------------------------------

def create_fashion_profile(
    person_image_path,
    garment_info,
    height,
    bust,
    waist,
    hip,
    occasion,
    fit_preference,
    garment_description
):

    skin = estimate_skin_tone(
        person_image_path
    )

    body = estimate_body_profile(
        bust,
        waist,
        hip
    )

    category = detect_garment_category(
        garment_description
    )

    garment_rgb = tuple(
        garment_info.get(
            "Dominant RGB",
            (128, 128, 128)
        )
    )

    undertone = skin["Undertone"]

    if undertone not in PALETTES:
        undertone = "Neutral"

    color_score, preferred_colors = color_harmony_score(
        garment_rgb,
        undertone
    )

    shape_score, shape_reasons = silhouette_score(
        body,
        category
    )

    occ_score, occ_reason = occasion_score(
        garment_description,
        occasion
    )

    # Transparent heuristic weighting.
    overall = round(
        color_score * 0.40 +
        shape_score * 0.35 +
        occ_score * 0.25
    )

    reasons = []

    reasons.append(
        f"Visible-tone palette estimate: "
        f"{skin['Tone']} / {skin['Undertone']}."
    )

    reasons.append(
        f"Body silhouette profile from measurements: "
        f"{body['Silhouette Profile']}."
    )

    reasons.extend(shape_reasons)

    reasons.append(
        f"Color harmony score is {color_score}/100 "
        f"based on the garment's dominant color."
    )

    reasons.append(
        occ_reason
    )

    reasons.append(
        f"Selected fit preference: {fit_preference}."
    )

    accessories = accessory_recommendations(
        occasion,
        category,
        undertone
    )

    return {
        "Profile": {
            "Height (cm)": float(height),
            "Body Silhouette": body["Silhouette Profile"],
            "Visible Skin Tone": skin["Tone"],
            "Visible Undertone": skin["Undertone"],
            "Skin Estimate Confidence": skin["Confidence"],
            "Fit Preference": fit_preference,
            "Garment Category": category,
            "Occasion": occasion
        },

        "Scores": {
            "Overall Style Match": overall,
            "Color Harmony": color_score,
            "Silhouette Compatibility": shape_score,
            "Occasion Compatibility": occ_score
        },

        "Preferred Color Palette": preferred_colors,

        "Why This Outfit Is Recommended": reasons,

        "Accessories": accessories
    }


# ---------------------------------------------------------
# FORMAT ACCESSORY LINKS FOR GRADIO
# ---------------------------------------------------------

def accessory_markdown(accessories):

    lines = [
        "## Recommended Accessories"
    ]

    for item in accessories:

        lines.append(
            f"### {item['Accessory']}"
        )

        lines.append(
            item["Why"]
        )

        lines.append(
            f"[Amazon Search]({item['Amazon Search']})  |  "
            f"[Myntra Search]({item['Myntra Search']})"
        )

    return "\n\n".join(lines)