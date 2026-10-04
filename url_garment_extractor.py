import gradio as gr
from pathlib import Path

from preprocess import preprocess_image
from image_validator import validate_image
from garment_analyzer import analyze_garment
from fashion_profile import create_fashion_profile, accessory_markdown
from tryon_engine import run_virtual_tryon
from url_garment_extractor import extract_garment


INPUT_DIR = Path("inputs")
OUTPUT_DIR = Path("outputs")

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def format_profile(profile):
    p = profile["Profile"]
    s = profile["Scores"]
    colors = ", ".join(profile["Preferred Color Palette"])

    return f"""## AI Fashion Profile

| Attribute | Result |
|---|---|
| Height | {p["Height (cm)"]:.0f} cm |
| Body Silhouette | {p["Body Silhouette"]} |
| Visible Skin Tone | {p["Visible Skin Tone"]} |
| Visible Undertone | {p["Visible Undertone"]} |
| Estimate Confidence | {p["Skin Estimate Confidence"]}% |
| Fit Preference | {p["Fit Preference"]} |
| Garment Category | {p["Garment Category"]} |
| Occasion | {p["Occasion"]} |

### Style Scores

- **Overall Style Match:** {s["Overall Style Match"]}/100
- **Color Harmony:** {s["Color Harmony"]}/100
- **Silhouette Compatibility:** {s["Silhouette Compatibility"]}/100
- **Occasion Compatibility:** {s["Occasion Compatibility"]}/100

### Preferred Colors

{colors}
"""


def format_reasons(profile):
    lines = ["## Why This Outfit Is Recommended", ""]
    for reason in profile["Why This Outfit Is Recommended"]:
        lines.append(f"- {reason}")
    return "\n".join(lines)


def format_occasion(profile):
    occasion = profile["Profile"]["Occasion"]

    places = {
        "College / Casual": [
            "College",
            "Shopping",
            "Cafe",
            "Day outing",
        ],
        "Office / Formal": [
            "Office",
            "Interview",
            "Business meeting",
            "Professional event",
        ],
        "Party / Evening": [
            "Party",
            "Dinner",
            "Evening event",
            "Celebration",
        ],
        "Traditional / Festive": [
            "Festival",
            "Wedding function",
            "Family function",
            "Traditional event",
        ],
    }

    tips = {
        "College / Casual":
            "Use comfortable footwear and simple everyday accessories.",
        "Office / Formal":
            "Use structured accessories and clean formal footwear.",
        "Party / Evening":
            "Use statement accessories and elevated footwear.",
        "Traditional / Festive":
            "Use traditional jewellery and ethnic footwear.",
    }

    items = places.get(occasion, ["General outing"])
    tip = tips.get(
        occasion,
        "Choose accessories suitable for the setting."
    )

    text = "## Where to Wear This Outfit\n\n"
    text += "\n".join(f"- {item}" for item in items)
    text += f"\n\n### Styling Tip\n{tip}"
    return text


def get_garment_from_source(source, garment_upload, garment_url):
    """
    Returns a local garment image path.

    Supported sources:
    1. Upload
    2. Product page URL
    3. Direct image URL

    Product pages may be blocked by the store.
    In that case the user can switch to Upload.
    """

    if source == "Upload Garment Image":

        if garment_upload is None:
            raise gr.Error(
                "Please upload a garment image."
            )

        path = INPUT_DIR / "garment.jpg"

        garment_upload.convert("RGB").save(
            path,
            quality=95
        )

        return str(path)

    if not garment_url or not garment_url.strip():
        raise gr.Error(
            "Please paste a product URL or image URL."
        )

    try:

        extracted_path = extract_garment(
            garment_url.strip()
        )

        return extracted_path

    except Exception as exc:

        message = str(exc)

        if "403" in message or "blocks automated access" in message:
            raise gr.Error(
                "This shopping site blocked automated access. "
                "Please use the Upload Garment Image option, "
                "or paste a direct product-image URL."
            )

        raise gr.Error(
            f"Could not extract the garment image: {message}"
        )


def run_fashion_studio(
    person_image,
    garment_upload,
    garment_source,
    garment_url,
    height,
    bust,
    waist,
    hip,
    occasion,
    fit_preference,
    garment_description,
    auto_mask,
    auto_crop,
    denoise_steps,
    seed,
):
    if person_image is None:
        raise gr.Error("Please upload a person image.")

    try:

        measurements = [height, bust, waist, hip]

        if any(value is None for value in measurements):
            raise gr.Error(
                "Please enter height, bust, waist and hip."
            )

        height = float(height)
        bust = float(bust)
        waist = float(waist)
        hip = float(hip)

        if min(height, bust, waist, hip) <= 0:
            raise gr.Error(
                "All measurements must be greater than zero."
            )

        if not garment_description or not garment_description.strip():
            raise gr.Error(
                "Please enter a garment description."
            )

        # -------------------------------------------------
        # 1. SAVE PERSON IMAGE
        # -------------------------------------------------

        person_path = INPUT_DIR / "person.jpg"

        person_image.convert("RGB").save(
            person_path,
            quality=95
        )

        # -------------------------------------------------
        # 2. GET GARMENT FROM UPLOAD OR URL
        # -------------------------------------------------

        garment_path = get_garment_from_source(
            garment_source,
            garment_upload,
            garment_url
        )

        # -------------------------------------------------
        # 3. VALIDATE INPUTS
        # -------------------------------------------------

        person_check = validate_image(
            str(person_path),
            "Person"
        )

        garment_check = validate_image(
            str(garment_path),
            "Garment"
        )

        if not person_check["valid"]:
            raise gr.Error(
                person_check["message"]
            )

        if not garment_check["valid"]:
            raise gr.Error(
                garment_check["message"]
            )

        # -------------------------------------------------
        # 4. PREPROCESSING
        # -------------------------------------------------

        preprocess_image(
            str(person_path),
            "person_processed.png"
        )

        preprocess_image(
            str(garment_path),
            "garment_processed.png"
        )

        processed_garment = (
            OUTPUT_DIR / "garment_processed.png"
        )

        processed_person = (
            OUTPUT_DIR / "person_processed.png"
        )

        # -------------------------------------------------
        # 5. GARMENT INTELLIGENCE
        # -------------------------------------------------

        garment_info = analyze_garment(
            str(processed_garment)
        )

        # -------------------------------------------------
        # 6. AI FASHION PROFILE
        # -------------------------------------------------

        profile = create_fashion_profile(
            person_image_path=str(
                processed_person
            ),
            garment_info=garment_info,
            height=height,
            bust=bust,
            waist=waist,
            hip=hip,
            occasion=occasion,
            fit_preference=fit_preference,
            garment_description=garment_description,
        )

        # -------------------------------------------------
        # 7. REAL IDM-VTON
        # -------------------------------------------------

        result_path, mask_path = run_virtual_tryon(
            str(processed_person),
            str(processed_garment),
            garment_description=garment_description,
            auto_mask=auto_mask,
            auto_crop=auto_crop,
            denoise_steps=int(denoise_steps),
            seed=int(seed),
        )

        # -------------------------------------------------
        # 8. FORMAT RESULTS
        # -------------------------------------------------

        source_text = garment_source

        if garment_source != "Upload Garment Image":
            source_text += f"\nSource URL: {garment_url}"

        status = f"""✅ COMPLETE

Garment Source:
{source_text}

Pipeline:
1. Person image validation
2. Garment acquisition
3. Image preprocessing
4. Garment intelligence
5. AI fashion profile
6. IDM-VTON virtual try-on
7. Style scoring
8. Occasion guidance
9. Accessory recommendations
"""

        return (
            result_path,
            mask_path,
            format_profile(profile),
            garment_info,
            format_reasons(profile),
            format_occasion(profile),
            accessory_markdown(profile["Accessories"]),
            status,
        )

    except gr.Error:
        raise

    except Exception as exc:

        raise gr.Error(
            f"Pipeline failed: "
            f"{type(exc).__name__}: {exc}"
        )


# =========================================================
# GRADIO UI
# =========================================================

with gr.Blocks(
    title="AI Virtual Fashion Studio"
) as demo:

    gr.Markdown(
        """
# 👗 AI Virtual Fashion Studio

### Your Personal AI Fashion Concierge

**Upload or Paste a Fashion Product URL → Analyze → Virtual Try-On → Style → Shop**
"""
    )

    # =====================================================
    # PERSONAL PROFILE
    # =====================================================

    with gr.Tab("👤 Personal Profile"):

        gr.Markdown(
            """
### Your Measurements

Enter approximate measurements in centimetres.
They are used for the fashion-profile heuristic.
"""
        )

        with gr.Row():

            height = gr.Number(
                value=165,
                label="Height (cm)",
                minimum=80,
                maximum=250,
            )

            bust = gr.Number(
                value=90,
                label="Bust / Chest (cm)",
                minimum=40,
                maximum=180,
            )

            waist = gr.Number(
                value=75,
                label="Waist (cm)",
                minimum=40,
                maximum=180,
            )

            hip = gr.Number(
                value=95,
                label="Hip (cm)",
                minimum=40,
                maximum=180,
            )

        with gr.Row():

            occasion = gr.Dropdown(
                choices=[
                    "College / Casual",
                    "Office / Formal",
                    "Party / Evening",
                    "Traditional / Festive",
                ],
                value="College / Casual",
                label="Occasion",
            )

            fit_preference = gr.Dropdown(
                choices=[
                    "Slim / Fitted",
                    "Regular",
                    "Relaxed / Oversized",
                ],
                value="Regular",
                label="Fit Preference",
            )

    # =====================================================
    # TRY-ON
    # =====================================================

    with gr.Tab("✨ Virtual Try-On"):

        with gr.Row():

            with gr.Column():

                gr.Markdown("## 1. Your Portrait")

                person_image = gr.Image(
                    type="pil",
                    label="Person Portrait",
                )

                gr.Markdown("## 2. Choose Garment Source")

                garment_source = gr.Radio(
                    choices=[
                        "Upload Garment Image",
                        "Product Page URL",
                        "Direct Image URL",
                    ],
                    value="Upload Garment Image",
                    label="Garment Source",
                )

                garment_upload = gr.Image(
                    type="pil",
                    label="Garment Image",
                )

                garment_url = gr.Textbox(
                    label="E-Commerce Product / Image URL",
                    placeholder=(
                        "Paste a supported product URL "
                        "or a direct .jpg/.png/.webp image URL"
                    ),
                )

                garment_description = gr.Textbox(
                    value="short sleeve t-shirt",
                    label="Garment Description",
                    placeholder=(
                        "Example: floral summer dress, "
                        "denim jacket, formal blazer"
                    ),
                )

                gr.Markdown("## 3. IDM-VTON Settings")

                auto_mask = gr.Checkbox(
                    value=True,
                    label="Automatic Mask",
                )

                auto_crop = gr.Checkbox(
                    value=False,
                    label="Automatic Crop",
                )

                denoise_steps = gr.Slider(
                    minimum=10,
                    maximum=50,
                    value=30,
                    step=1,
                    label="Denoising Steps",
                )

                seed = gr.Number(
                    value=42,
                    precision=0,
                    label="Seed",
                )

                generate_button = gr.Button(
                    "✨ Analyze & Generate Virtual Try-On",
                    variant="primary",
                )

            with gr.Column():

                gr.Markdown(
                    "## 4. AI Virtual Try-On"
                )

                result_image = gr.Image(
                    type="filepath",
                    label="Virtual Try-On Result",
                )

                mask_image = gr.Image(
                    type="filepath",
                    label="Generated Mask",
                )

                status_box = gr.Textbox(
                    label="Pipeline Status",
                    lines=12,
                )

    # =====================================================
    # AI PROFILE
    # =====================================================

    with gr.Tab("🧠 AI Fashion Profile"):

        profile_output = gr.Markdown(
            "Generate a result to see your AI fashion profile."
        )

        garment_output = gr.JSON(
            label="Garment Intelligence"
        )

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    with gr.Tab("💡 Recommendations"):

        recommendation_output = gr.Markdown(
            "Generate a result to see the recommendation explanation."
        )

        occasion_output = gr.Markdown(
            "Generate a result to see where the outfit can be worn."
        )

    # =====================================================
    # ACCESSORIES
    # =====================================================

    with gr.Tab("🛍️ Accessories & Shopping"):

        accessories_output = gr.Markdown(
            "Generate a result to see accessory recommendations."
        )

        gr.Markdown(
            """
### Shopping Links

The current implementation generates search links for
recommended accessory categories. Exact products, stock,
prices and availability can change.
"""
        )

    # =====================================================
    # PIPELINE EVENT
    # =====================================================

    generate_button.click(
        fn=run_fashion_studio,
        inputs=[
            person_image,
            garment_upload,
            garment_source,
            garment_url,
            height,
            bust,
            waist,
            hip,
            occasion,
            fit_preference,
            garment_description,
            auto_mask,
            auto_crop,
            denoise_steps,
            seed,
        ],
        outputs=[
            result_image,
            mask_image,
            profile_output,
            garment_output,
            recommendation_output,
            occasion_output,
            accessories_output,
            status_box,
        ],
    )

    # =====================================================
    # FOOTER
    # =====================================================

    gr.Markdown(
        """
---

### AI Virtual Fashion Studio

**Person + Garment / Product URL**
→ Validation
→ Preprocessing
→ Garment Intelligence
→ Personal Fashion Profile
→ IDM-VTON
→ Explainable Style Scores
→ Occasion Guidance
→ Accessories & Shopping

*URL extraction works only when the target site permits the
request or when a direct image URL is supplied.*
"""
    )


if __name__ == "__main__":
    demo.launch()