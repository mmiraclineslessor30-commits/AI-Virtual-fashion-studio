import gradio as gr
from pathlib import Path

from preprocess import preprocess_image
from image_validator import validate_image
from garment_analyzer import analyze_garment
from fashion_profile import create_fashion_profile, accessory_markdown
from tryon_engine import run_virtual_tryon
from database import SessionLocal, TryOnHistory, init_db


# ============================================================
# DIRECTORIES
# ============================================================

INPUT_DIR = Path("inputs")
OUTPUT_DIR = Path("outputs")

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# DATABASE
# ============================================================

init_db()


# ============================================================
# CUSTOM CSS
# ============================================================

CUSTOM_CSS = """
body {
    background:
        radial-gradient(circle at top left, #fff0f5 0%, transparent 35%),
        radial-gradient(circle at top right, #eee9ff 0%, transparent 35%),
        linear-gradient(135deg, #faf7ff 0%, #f7fbff 100%);
}

.gradio-container {
    max-width: 1450px !important;
    margin: auto !important;
}

#hero {
    padding: 45px 30px;
    border-radius: 30px;
    margin-bottom: 25px;
    text-align: center;
    color: white;
    background:
        linear-gradient(
            135deg,
            #ff4f81 0%,
            #b14cff 50%,
            #6d5dfc 100%
        );
    box-shadow:
        0 20px 50px rgba(105, 70, 180, 0.25);
    animation: heroFloat 4s ease-in-out infinite;
}

#hero h1 {
    font-size: 46px;
    font-weight: 900;
    margin-bottom: 8px;
    letter-spacing: 1px;
}

#hero h2 {
    font-size: 24px;
    font-weight: 700;
    margin-top: 5px;
}

#hero p {
    font-size: 17px;
    opacity: 0.95;
}

.section-card {
    border-radius: 24px !important;
    border: 1px solid rgba(130, 100, 200, 0.12) !important;
    box-shadow: 0 12px 35px rgba(50, 30, 100, 0.08) !important;
    background: rgba(255, 255, 255, 0.78) !important;
}

.feature-card {
    border-radius: 20px !important;
    padding: 18px !important;
    min-height: 130px;
    transition: all 0.25s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(80, 50, 150, 0.15);
}

.primary-btn {
    border-radius: 18px !important;
    font-size: 17px !important;
    font-weight: 800 !important;
    min-height: 55px !important;
    background: linear-gradient(135deg, #ff4f81, #8b5cf6) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 10px 25px rgba(140, 70, 200, 0.25);
    transition: all 0.25s ease !important;
}

.primary-btn:hover {
    transform: translateY(-3px) scale(1.01);
    box-shadow: 0 15px 35px rgba(140, 70, 200, 0.35);
}

.secondary-btn {
    border-radius: 15px !important;
    font-weight: 700 !important;
}

.tab-nav button {
    font-weight: 750 !important;
    font-size: 15px !important;
}

.result-box {
    border-radius: 24px !important;
    overflow: hidden !important;
    box-shadow: 0 15px 40px rgba(50, 30, 100, 0.12);
}

.score-card {
    border-radius: 18px;
    padding: 20px;
    background: white;
    box-shadow: 0 8px 25px rgba(50, 30, 100, 0.08);
}

.footer {
    text-align: center;
    padding: 25px;
    margin-top: 25px;
    border-radius: 20px;
    background: linear-gradient(135deg, #181329, #30204d);
    color: white;
}

@keyframes heroFloat {
    0%, 100% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-4px);
    }
}

@media (max-width: 900px) {
    #hero h1 {
        font-size: 32px;
    }

    #hero h2 {
        font-size: 20px;
    }
}
"""


# ============================================================
# PROFILE FORMATTER
# ============================================================

def format_profile(profile):
    p = profile["Profile"]
    s = profile["Scores"]

    colors = ", ".join(
        profile.get("Preferred Color Palette", [])
    )

    return f"""
## AI Style Profile

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

### Style Compatibility

- Overall Style Match: **{s["Overall Style Match"]}/100**
- Color Harmony: **{s["Color Harmony"]}/100**
- Silhouette Compatibility: **{s["Silhouette Compatibility"]}/100**
- Occasion Compatibility: **{s["Occasion Compatibility"]}/100**

### Preferred Colors

{colors}
"""


# ============================================================
# RECOMMENDATION FORMATTER
# ============================================================

def format_reasons(profile):
    lines = [
        "## Why This Outfit Works",
        ""
    ]

    reasons = profile.get(
        "Why This Outfit Is Recommended",
        []
    )

    if not reasons:
        lines.append(
            "- The outfit was evaluated using the available "
            "garment, measurement and occasion information."
        )
    else:
        for reason in reasons:
            lines.append(f"- {reason}")

    return "\n".join(lines)


# ============================================================
# OCCASION FORMATTER
# ============================================================

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

    items = places.get(
        occasion,
        ["General outing"]
    )

    tip = tips.get(
        occasion,
        "Choose accessories suitable for the setting."
    )

    text = "## Where to Wear This Outfit\n\n"

    text += "\n".join(
        f"- {item}"
        for item in items
    )

    text += (
        f"\n\n### Styling Tip\n{tip}"
    )

    return text


# ============================================================
# HISTORY
# ============================================================

def load_history():
    db = SessionLocal()

    try:
        records = (
            db.query(TryOnHistory)
            .order_by(TryOnHistory.id.desc())
            .all()
        )

        if not records:
            return "No try-on history found."

        lines = []

        for record in records:
            lines.append(
                f"""
ID: {record.id}
Garment: {record.garment_name}
Occasion: {record.occasion}
Style Score: {record.style_score}
Result Image: {record.result_image}
Created: {record.created_at}
----------------------------------------
"""
            )

        return "\n".join(lines)

    finally:
        db.close()


# ============================================================
# MAIN FASHION PIPELINE
# ============================================================

def run_fashion_studio(
    person_image,
    garment_image,
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
        raise gr.Error(
            "Please upload a person image."
        )

    if garment_image is None:
        raise gr.Error(
            "Please upload a garment image."
        )

    try:

        # ----------------------------------------------------
        # VALIDATE MEASUREMENTS
        # ----------------------------------------------------

        measurements = [
            height,
            bust,
            waist,
            hip
        ]

        if any(
            value is None
            for value in measurements
        ):
            raise gr.Error(
                "Please enter height, bust, waist and hip."
            )

        height = float(height)
        bust = float(bust)
        waist = float(waist)
        hip = float(hip)

        if min(
            height,
            bust,
            waist,
            hip
        ) <= 0:

            raise gr.Error(
                "All measurements must be greater than zero."
            )

        # ----------------------------------------------------
        # VALIDATE DESCRIPTION
        # ----------------------------------------------------

        if (
            not garment_description
            or not garment_description.strip()
        ):
            raise gr.Error(
                "Please enter a garment description."
            )

        # ----------------------------------------------------
        # SAVE INPUT IMAGES
        # ----------------------------------------------------

        person_path = (
            INPUT_DIR / "person.jpg"
        )

        garment_path = (
            INPUT_DIR / "garment.jpg"
        )

        person_image.convert(
            "RGB"
        ).save(
            person_path,
            quality=95
        )

        garment_image.convert(
            "RGB"
        ).save(
            garment_path,
            quality=95
        )

        # ----------------------------------------------------
        # IMAGE VALIDATION
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # PREPROCESSING
        # ----------------------------------------------------

        preprocess_image(
            str(person_path),
            "person_processed.png"
        )

        preprocess_image(
            str(garment_path),
            "garment_processed.png"
        )

        # ----------------------------------------------------
        # GARMENT INTELLIGENCE
        # ----------------------------------------------------

        garment_info = analyze_garment(
            str(
                OUTPUT_DIR /
                "garment_processed.png"
            )
        )

        # ----------------------------------------------------
        # AI FASHION PROFILE
        # ----------------------------------------------------

        profile = create_fashion_profile(
            person_image_path=str(
                OUTPUT_DIR /
                "person_processed.png"
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

        # ----------------------------------------------------
        # IDM-VTON
        # ----------------------------------------------------

        result_path, mask_path = run_virtual_tryon(
            str(
                OUTPUT_DIR /
                "person_processed.png"
            ),
            str(
                OUTPUT_DIR /
                "garment_processed.png"
            ),
            garment_description=garment_description,
            auto_mask=auto_mask,
            auto_crop=auto_crop,
            denoise_steps=int(
                denoise_steps
            ),
            seed=int(seed),
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = """
COMPLETE

1. Image validation
2. Image preprocessing
3. Garment intelligence
4. AI fashion profile
5. IDM-VTON virtual try-on
6. Style scoring
7. Occasion guidance
8. Accessory recommendations
"""

        return (
            result_path,
            mask_path,
            format_profile(profile),
            garment_info,
            format_reasons(profile),
            format_occasion(profile),
            accessory_markdown(
                profile["Accessories"]
            ),
            status,
        )

    except gr.Error:
        raise

    except Exception as exc:
        raise gr.Error(
            f"Pipeline failed: "
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# GRADIO APPLICATION
# ============================================================

with gr.Blocks(
    title="AI Virtual Fashion Studio"
) as demo:

    # ========================================================
    # HERO
    # ========================================================

    gr.Markdown(
        """
<div id="hero">

<h1>AI VIRTUAL FASHION STUDIO</h1>

<h2>Your Personal AI Fashion Assistant</h2>

<p>
Try it. Understand it. Style it. Wear it.
</p>

<p>
AI Virtual Try-On | Style Intelligence | Smart Recommendations
</p>

</div>
"""
    )

    # ========================================================
    # HOME FEATURES
    # ========================================================

    gr.Markdown(
        """
## What You Can Do

Use the complete AI fashion workflow to analyze an outfit,
generate a virtual try-on and build a personalized styling profile.
"""
    )

    with gr.Row():

        with gr.Column(
            elem_classes="feature-card"
        ):

            gr.Markdown(
                """
### Virtual Try-On

Upload your portrait and garment to generate
an AI-powered outfit preview.
"""
            )

        with gr.Column(
            elem_classes="feature-card"
        ):

            gr.Markdown(
                """
### Style Intelligence

Analyze body measurements, garment information,
fit preference and styling compatibility.
"""
            )

        with gr.Column(
            elem_classes="feature-card"
        ):

            gr.Markdown(
                """
### Smart Recommendations

Understand colour harmony, silhouette compatibility,
occasion compatibility and overall style matching.
"""
            )

        with gr.Column(
            elem_classes="feature-card"
        ):

            gr.Markdown(
                """
### Complete the Look

Get accessory and styling suggestions for
shoes, bags, watches and jewellery.
"""
            )

    # ========================================================
    # PERSONAL PROFILE
    # ========================================================

    with gr.Tab("Personal Profile"):

        gr.Markdown(
            """
## Personal Fashion Profile

Enter your measurements and styling preferences.
These values are used by the fashion analysis pipeline.
"""
        )

        with gr.Row():

            with gr.Column(
                elem_classes="section-card"
            ):

                height = gr.Number(
                    value=165,
                    label="Height (cm)",
                    minimum=80,
                    maximum=250,
                )

            with gr.Column(
                elem_classes="section-card"
            ):

                bust = gr.Number(
                    value=90,
                    label="Bust / Chest (cm)",
                    minimum=40,
                    maximum=180,
                )

            with gr.Column(
                elem_classes="section-card"
            ):

                waist = gr.Number(
                    value=75,
                    label="Waist (cm)",
                    minimum=40,
                    maximum=180,
                )

            with gr.Column(
                elem_classes="section-card"
            ):

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

    # ========================================================
    # VIRTUAL TRY-ON
    # ========================================================

    with gr.Tab("Virtual Try-On"):

        with gr.Row():

            # ------------------------------------------------
            # INPUT COLUMN
            # ------------------------------------------------

            with gr.Column(
                scale=1,
                elem_classes="section-card"
            ):

                gr.Markdown(
                    """
## 1. Upload Your Inputs

Add a person image and a garment image.
"""
                )

                person_image = gr.Image(
                    type="pil",
                    label="Person Portrait",
                )

                garment_image = gr.Image(
                    type="pil",
                    label="Garment",
                )

                garment_description = gr.Textbox(
                    value="short sleeve t-shirt",
                    label="Garment Description",
                    placeholder=(
                        "Example: floral summer dress, "
                        "denim jacket, formal blazer"
                    ),
                )

                gr.Markdown(
                    """
## 2. IDM-VTON Settings
"""
                )

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
                    "Generate Complete Fashion Analysis",
                    variant="primary",
                    elem_classes="primary-btn",
                )

            # ------------------------------------------------
            # RESULT COLUMN
            # ------------------------------------------------

            with gr.Column(
                scale=1,
                elem_classes="section-card"
            ):

                gr.Markdown(
                    """
## 3. AI Virtual Try-On Result

Your generated result will appear here.
"""
                )

                result_image = gr.Image(
                    type="filepath",
                    label="AI Virtual Try-On Result",
                    elem_classes="result-box",
                )

                mask_image = gr.Image(
                    type="filepath",
                    label="Generated Human Mask",
                    elem_classes="result-box",
                )

                status_box = gr.Textbox(
                    label="Pipeline Status",
                    lines=12,
                )

    # ========================================================
    # AI FASHION PROFILE
    # ========================================================

    with gr.Tab("AI Fashion Profile"):

        gr.Markdown(
            """
## Your Personal Style Intelligence

The AI profile combines your supplied measurements,
garment analysis and selected occasion.
"""
        )

        profile_output = gr.Markdown(
            """
Generate a result to see your AI fashion profile.
"""
        )

        garment_output = gr.JSON(
            label="Garment Intelligence"
        )

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    with gr.Tab("Recommendations"):

        gr.Markdown(
            """
## Smart Styling Recommendations

Understand why the selected outfit works and
where it can be worn.
"""
        )

        recommendation_output = gr.Markdown(
            """
Generate a result to see outfit recommendations.
"""
        )

        occasion_output = gr.Markdown(
            """
Generate a result to see occasion guidance.
"""
        )

    # ========================================================
    # ACCESSORIES
    # ========================================================

    with gr.Tab("Accessories and Shopping"):

        gr.Markdown(
            """
## Complete the Look

Discover accessories that can complement the outfit.
"""
        )

        accessories_output = gr.Markdown(
            """
Generate a result to see accessory recommendations
and shopping links.
"""
        )

        gr.Markdown(
            """
### Shopping Note

Links are search links rather than guaranteed exact
product matches. Availability and pricing may change.
"""
        )

    # ========================================================
    # HISTORY
    # ========================================================

    with gr.Tab("Try-On History"):

        gr.Markdown(
            """
## Saved Try-On Sessions

Review previous generated try-on sessions.
"""
        )

        history_output = gr.Textbox(
            label="Saved Try-On History",
            lines=18,
            value=(
                "Click Refresh History to load "
                "saved looks."
            ),
        )

        refresh_history = gr.Button(
            "Refresh History",
            elem_classes="secondary-btn",
        )

        refresh_history.click(
            fn=load_history,
            outputs=history_output,
        )

    # ========================================================
    # MAIN BUTTON EVENT
    # ========================================================

    generate_button.click(
        fn=run_fashion_studio,
        inputs=[
            person_image,
            garment_image,
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

    # ========================================================
    # FOOTER
    # ========================================================

    gr.Markdown(
        """
<div class="footer">

<h2>AI Virtual Fashion Studio</h2>

<p>
Python | PyTorch | Computer Vision | Deep Learning |
IDM-VTON | Image Processing | Gradio
</p>

<p>
Person + Garment -> Validation -> Preprocessing ->
Garment Intelligence -> Fashion Profile ->
Virtual Try-On -> Style Analysis -> Occasion ->
Accessories
</p>

</div>
"""
    )


# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":
    demo.launch(
        css=CUSTOM_CSS,
        server_name="127.0.0.1",
        server_port=7860,
    )