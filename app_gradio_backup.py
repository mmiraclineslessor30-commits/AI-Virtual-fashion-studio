import gradio as gr
from pathlib import Path

from preprocess import preprocess_image
from image_validator import validate_image
from garment_analyzer import analyze_garment
from fashion_profile import create_fashion_profile, accessory_markdown
from tryon_engine import run_virtual_tryon
from database import SessionLocal, TryOnHistory, init_db

# ============================================================

# PROJECT DIRECTORIES

# ============================================================

INPUT_DIR = Path("inputs")
OUTPUT_DIR = Path("outputs")

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================

# PREMIUM UI CSS

# ============================================================

CUSTOM_CSS = r"""
/* ==========================================================
GLOBAL
========================================================== */

:root {
--bg-main: #070711;
--bg-card: rgba(255,255,255,0.055);
--border: rgba(255,255,255,0.11);
--text: #f7f7fb;
--muted: #a7a7b7;
--pink: #ff4fa3;
--purple: #8c6cff;
--blue: #43c7ff;
}

body {
background:
radial-gradient(
circle at 10% 10%,
rgba(255, 79, 163, 0.16),
transparent 28%
),
radial-gradient(
circle at 90% 15%,
rgba(91, 94, 255, 0.18),
transparent 30%
),
radial-gradient(
circle at 50% 100%,
rgba(67, 199, 255, 0.10),
transparent 35%
),
#070711 !important;
}

/* Main Gradio container */

.gradio-container {
max-width: 1480px !important;
margin: auto !important;
padding: 24px !important;
}

/* ==========================================================
HERO
========================================================== */

.hero {
position: relative;
overflow: hidden;
padding: 65px 55px;
margin-bottom: 28px;
border-radius: 32px;

```
background:
    linear-gradient(
        135deg,
        rgba(255,255,255,0.10),
        rgba(255,255,255,0.025)
    );

border: 1px solid rgba(255,255,255,0.13);

box-shadow:
    0 30px 100px rgba(0,0,0,0.45),
    inset 0 1px 0 rgba(255,255,255,0.08);

backdrop-filter: blur(22px);

animation: heroReveal 0.9s ease-out;
```

}

.hero::before {
content: "";
position: absolute;

```
width: 280px;
height: 280px;

right: -90px;
top: -120px;

border-radius: 50%;

background:
    radial-gradient(
        circle,
        rgba(255,79,163,0.32),
        transparent 70%
    );

animation: floatingOrb 7s ease-in-out infinite;
```

}

.hero::after {
content: "";
position: absolute;

```
width: 220px;
height: 220px;

left: -100px;
bottom: -130px;

border-radius: 50%;

background:
    radial-gradient(
        circle,
        rgba(67,199,255,0.20),
        transparent 70%
    );

animation: floatingOrb 9s ease-in-out infinite reverse;
```

}

.hero-badge {
display: inline-block;

```
padding: 8px 16px;

border-radius: 999px;

font-size: 12px;
font-weight: 700;
letter-spacing: 1.5px;

color: #ffffff;

background:
    linear-gradient(
        90deg,
        rgba(255,79,163,0.22),
        rgba(140,108,255,0.22)
    );

border: 1px solid rgba(255,255,255,0.15);

margin-bottom: 18px;
```

}

.hero-title {
position: relative;
z-index: 2;

```
font-size: 58px !important;
line-height: 1.05 !important;
font-weight: 900 !important;

letter-spacing: -2px;

background:
    linear-gradient(
        90deg,
        #ff4fa3,
        #b06cff,
        #43c7ff
    );

-webkit-background-clip: text;
-webkit-text-fill-color: transparent;

margin-bottom: 18px;
```

}

.hero-subtitle {
position: relative;
z-index: 2;

```
max-width: 850px;

font-size: 20px !important;
line-height: 1.7 !important;

color: #c8c8d5 !important;
```

}

/* ==========================================================
FEATURE CARDS
========================================================== */

.feature-card {
min-height: 175px;

```
padding: 27px;

border-radius: 24px;

background:
    linear-gradient(
        145deg,
        rgba(255,255,255,0.085),
        rgba(255,255,255,0.025)
    );

border: 1px solid var(--border);

box-shadow:
    0 15px 45px rgba(0,0,0,0.20);

transition:
    transform 0.35s ease,
    border-color 0.35s ease,
    box-shadow 0.35s ease;

animation: cardReveal 0.7s ease-out;
```

}

.feature-card:hover {
transform: translateY(-8px);

```
border-color:
    rgba(255,79,163,0.40);

box-shadow:
    0 25px 65px rgba(255,79,163,0.12);
```

}

.feature-icon {
font-size: 32px;
margin-bottom: 10px;
}

.feature-title {
font-size: 19px;
font-weight: 800;
margin-bottom: 8px;
}

.feature-text {
color: var(--muted);
line-height: 1.6;
}

/* ==========================================================
SECTION HEADERS
========================================================== */

.section-header {
margin-top: 10px;
margin-bottom: 18px;

```
font-size: 28px !important;
font-weight: 850 !important;

color: #ffffff;
```

}

.section-subtitle {
color: var(--muted);
margin-bottom: 20px;
}

/* ==========================================================
GLASS PANELS
========================================================== */

.glass-panel {
padding: 25px;

```
border-radius: 24px;

background:
    rgba(255,255,255,0.045);

border:
    1px solid rgba(255,255,255,0.09);

box-shadow:
    0 18px 55px rgba(0,0,0,0.22);

backdrop-filter: blur(16px);
```

}

/* ==========================================================
TABS
========================================================== */

button[role="tab"] {
border-radius: 13px !important;

```
margin: 4px !important;

border: 1px solid transparent !important;

transition:
    all 0.25s ease !important;
```

}

button[role="tab"]:hover {
background:
rgba(255,255,255,0.075) !important;

```
transform:
    translateY(-1px);
```

}

/* ==========================================================
INPUTS
========================================================== */

input,
textarea,
select,
.gr-input {
border-radius: 13px !important;
}

input:focus,
textarea:focus,
select:focus {
border-color:
rgba(255,79,163,0.60) !important;

```
box-shadow:
    0 0 0 3px rgba(255,79,163,0.10) !important;
```

}

/* ==========================================================
PRIMARY BUTTON
========================================================== */

#generate-btn {
min-height: 62px;

```
border: none !important;

border-radius: 17px !important;

font-size: 17px !important;
font-weight: 800 !important;

color: #ffffff !important;

background:
    linear-gradient(
        90deg,
        #ff3f9d,
        #8d62ff,
        #3ec9ff
    ) !important;

box-shadow:
    0 14px 38px rgba(140,108,255,0.30);

transition:
    transform 0.25s ease,
    box-shadow 0.25s ease !important;
```

}

#generate-btn:hover {
transform:
translateY(-3px) scale(1.01);

```
box-shadow:
    0 20px 48px rgba(255,79,163,0.35);
```

}

#generate-btn:active {
transform:
translateY(0) scale(0.99);
}

/* ==========================================================
SECONDARY BUTTONS
========================================================== */

button {
border-radius: 13px !important;

```
transition:
    transform 0.2s ease,
    box-shadow 0.2s ease !important;
```

}

button:hover {
transform: translateY(-2px);
}

/* ==========================================================
OUTPUTS
========================================================== */

.output-card {
padding: 24px;

```
border-radius: 23px;

background:
    rgba(255,255,255,0.045);

border:
    1px solid rgba(255,255,255,0.09);

box-shadow:
    0 18px 50px rgba(0,0,0,0.22);
```

}

/* ==========================================================
SCORE / RESULT MARKDOWN
========================================================== */

.pro-result {
padding: 25px;

```
border-radius: 22px;

background:
    linear-gradient(
        135deg,
        rgba(255,79,163,0.08),
        rgba(140,108,255,0.07),
        rgba(67,199,255,0.05)
    );

border:
    1px solid rgba(255,255,255,0.10);
```

}

.pro-result table {
width: 100%;
}

.pro-result th {
color: #ffffff;
}

.pro-result td {
color: #c7c7d4;
}

/* ==========================================================
PIPELINE
========================================================== */

.pipeline {
text-align: center;

```
padding: 20px;

border-radius: 19px;

background:
    rgba(255,255,255,0.045);

border:
    1px solid rgba(255,255,255,0.08);

transition:
    all 0.3s ease;
```

}

.pipeline:hover {
transform:
translateY(-5px);

```
background:
    rgba(255,255,255,0.075);
```

}

.pipeline-number {
display: inline-flex;

```
width: 38px;
height: 38px;

align-items: center;
justify-content: center;

border-radius: 50%;

font-weight: 800;

background:
    linear-gradient(
        135deg,
        #ff4fa3,
        #8c6cff
    );

color: #ffffff;

margin-bottom: 10px;
```

}

/* ==========================================================
FOOTER
========================================================== */

.footer {
text-align: center;

```
margin-top: 35px;
padding: 30px;

border-top:
    1px solid rgba(255,255,255,0.08);

color: #858596;

font-size: 13px;
```

}

/* ==========================================================
ANIMATIONS
========================================================== */

@keyframes heroReveal {

```
from {
    opacity: 0;
    transform: translateY(25px);
}

to {
    opacity: 1;
    transform: translateY(0);
}
```

}

@keyframes cardReveal {

```
from {
    opacity: 0;
    transform: translateY(18px);
}

to {
    opacity: 1;
    transform: translateY(0);
}
```

}

@keyframes floatingOrb {

```
0% {
    transform: translate(0, 0);
}

50% {
    transform: translate(25px, 20px);
}

100% {
    transform: translate(0, 0);
}
```

}

/* ==========================================================
MOBILE
========================================================== */

@media (max-width: 800px) {

```
.gradio-container {
    padding: 12px !important;
}

.hero {
    padding: 35px 25px;
}

.hero-title {
    font-size: 38px !important;
}

.hero-subtitle {
    font-size: 16px !important;
}
```

}
"""

# ============================================================

# PROFILE FORMATTER

# ============================================================

def format_profile(profile):

```
p = profile["Profile"]
s = profile["Scores"]

colors = ", ".join(
    profile.get("Preferred Color Palette", [])
)

return f"""
```

<div class="pro-result">

## AI Style Intelligence

| Attribute           | Result                           |
| ------------------- | -------------------------------- |
| Height              | {p["Height (cm)"]:.0f} cm        |
| Body Silhouette     | {p["Body Silhouette"]}           |
| Visible Skin Tone   | {p["Visible Skin Tone"]}         |
| Visible Undertone   | {p["Visible Undertone"]}         |
| Estimate Confidence | {p["Skin Estimate Confidence"]}% |
| Fit Preference      | {p["Fit Preference"]}            |
| Garment Category    | {p["Garment Category"]}          |
| Occasion            | {p["Occasion"]}                  |

### Style Compatibility

* Overall Style Match: **{s["Overall Style Match"]}/100**
* Color Harmony: **{s["Color Harmony"]}/100**
* Silhouette Compatibility: **{s["Silhouette Compatibility"]}/100**
* Occasion Compatibility: **{s["Occasion Compatibility"]}/100**

### Preferred Color Palette

{colors}

</div>
"""

# ============================================================

# RECOMMENDATION FORMATTER

# ============================================================

def format_reasons(profile):

```
lines = [
    '<div class="pro-result">',
    "## Why This Outfit Works",
    "",
]

for reason in profile["Why This Outfit Is Recommended"]:
    lines.append(f"- {reason}")

lines.append("")
lines.append("</div>")

return "\n".join(lines)
```

# ============================================================

# OCCASION FORMATTER

# ============================================================

def format_occasion(profile):

```
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

text = [
    '<div class="pro-result">',
    "## Where to Wear This Outfit",
    "",
]

for item in items:
    text.append(f"- {item}")

text.extend(
    [
        "",
        "### Styling Tip",
        tip,
        "",
        "</div>",
    ]
)

return "\n".join(text)
```

# ============================================================

# MAIN ML PIPELINE

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

```
if person_image is None:
    raise gr.Error(
        "Please upload a person image."
    )

if garment_image is None:
    raise gr.Error(
        "Please upload a garment image."
    )

try:

    measurements = [
        height,
        bust,
        waist,
        hip,
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
        hip,
    ) <= 0:
        raise gr.Error(
            "All measurements must be greater than zero."
        )

    if (
        not garment_description
        or not garment_description.strip()
    ):
        raise gr.Error(
            "Please enter a garment description."
        )

    # ----------------------------------------------------
    # Save uploaded images
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
        quality=95,
    )

    garment_image.convert(
        "RGB"
    ).save(
        garment_path,
        quality=95,
    )

    # ----------------------------------------------------
    # Image validation
    # ----------------------------------------------------

    person_check = validate_image(
        str(person_path),
        "Person",
    )

    garment_check = validate_image(
        str(garment_path),
        "Garment",
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
    # Preprocessing
    # ----------------------------------------------------

    preprocess_image(
        str(person_path),
        "person_processed.png",
    )

    preprocess_image(
        str(garment_path),
        "garment_processed.png",
    )

    # ----------------------------------------------------
    # Garment intelligence
    # ----------------------------------------------------

    garment_info = analyze_garment(
        str(
            OUTPUT_DIR /
            "garment_processed.png"
        )
    )

    # ----------------------------------------------------
    # AI fashion profile
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

    result_path, mask_path = (
        run_virtual_tryon(
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
    )

    # ----------------------------------------------------
    # Pipeline status
    # ----------------------------------------------------

    status = """
```

COMPLETE

01  Image validation
02  Image preprocessing
03  Garment intelligence
04  AI fashion profile
05  IDM-VTON virtual try-on
06  Style compatibility analysis
07  Occasion intelligence
08  Accessory recommendations
"""

```
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
```

# ============================================================

# DATABASE

# ============================================================

init_db()

def load_history():

```
db = SessionLocal()

try:

    records = (
        db.query(TryOnHistory)
        .order_by(
            TryOnHistory.id.desc()
        )
        .all()
    )

    if not records:
        return "No try-on history found."

    lines = []

    for record in records:

        lines.append(
            f"""
```

ID: {record.id}
Garment: {record.garment_name}
Occasion: {record.occasion}
Style Score: {record.style_score}
Result Image: {record.result_image}
Created: {record.created_at}
----------------------------

"""
)

```
    return "\n".join(lines)

finally:

    db.close()
```

# ============================================================

# GRADIO APPLICATION

# ============================================================

with gr.Blocks(
title="AI Virtual Fashion Studio",
) as demo:

```
# ========================================================
# HERO SECTION
# ========================================================

gr.HTML(
    """
```

<div class="hero">

<div class="hero-badge">
AI FASHION INTELLIGENCE PLATFORM
</div>

<div class="hero-title">
AI Virtual Fashion Studio
</div>

<div class="hero-subtitle">
A flagship machine-learning fashion platform that combines
virtual try-on, computer vision, garment intelligence,
silhouette analysis and personalized styling.
</div>

</div>
"""
    )

```
# ========================================================
# FEATURE CARDS
# ========================================================

with gr.Row():

    with gr.Column():

        gr.HTML(
            """
```

<div class="feature-card">

<div class="feature-icon">V</div>

<div class="feature-title">
Virtual Try-On
</div>

<div class="feature-text">
Experience garments virtually using an
AI-powered try-on pipeline.
</div>

</div>
"""
            )

```
    with gr.Column():

        gr.HTML(
            """
```

<div class="feature-card">

<div class="feature-icon">AI</div>

<div class="feature-title">
Style Intelligence
</div>

<div class="feature-text">
Analyze silhouette, fit, colour harmony
and occasion compatibility.
</div>

</div>
"""
            )

```
    with gr.Column():

        gr.HTML(
            """
```

<div class="feature-card">

<div class="feature-icon">ML</div>

<div class="feature-title">
Smart Recommendations
</div>

<div class="feature-text">
Understand why an outfit works and receive
personalized styling guidance.
</div>

</div>
"""
            )

```
    with gr.Column():

        gr.HTML(
            """
```

<div class="feature-card">

<div class="feature-icon">+</div>

<div class="feature-title">
Complete the Look
</div>

<div class="feature-text">
Discover complementary accessories,
footwear and styling ideas.
</div>

</div>
"""
            )

```
# ========================================================
# TABS
# ========================================================

with gr.Tab(
    "Personal Profile"
):

    gr.Markdown(
        """
```

## Personal Style Profile

Enter your measurements and styling preferences.
These values are used by the fashion intelligence pipeline
for silhouette and fit analysis.
"""
)

```
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

# ========================================================
# VIRTUAL TRY-ON
# ========================================================

with gr.Tab(
    "Virtual Try-On"
):

    gr.Markdown(
        """
```

## AI Virtual Try-On

Upload a person image and a garment image.
The pipeline validates, preprocesses and analyzes the inputs
before generating the virtual try-on result.
"""
)

```
    with gr.Row():

        with gr.Column(
            scale=1
        ):

            gr.Markdown(
                "### 01. Input Images"
            )

            person_image = gr.Image(
                type="pil",
                label="Person Portrait",
            )

            garment_image = gr.Image(
                type="pil",
                label="Garment Image",
            )

            garment_description = gr.Textbox(
                value="short sleeve t-shirt",
                label="Garment Description",
                placeholder=(
                    "Example: black oversized t-shirt"
                ),
            )

            gr.Markdown(
                "### 02. Generation Controls"
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
                label="Generation Seed",
            )

            generate_button = gr.Button(
                "Generate AI Fashion Analysis",
                variant="primary",
                elem_id="generate-btn",
            )

        with gr.Column(
            scale=1
        ):

            gr.Markdown(
                "### 03. AI Result"
            )

            result_image = gr.Image(
                type="filepath",
                label="Virtual Try-On Result",
            )

            mask_image = gr.Image(
                type="filepath",
                label="Generated Human Mask",
            )

            status_box = gr.Textbox(
                label="Pipeline Status",
                lines=12,
            )

# ========================================================
# AI PROFILE
# ========================================================

with gr.Tab(
    "AI Style Profile"
):

    profile_output = gr.Markdown(
        """
```

## AI Style Intelligence

Generate a look to see your personalized
fashion profile.
"""
)

```
    garment_output = gr.JSON(
        label="Garment Intelligence",
    )

# ========================================================
# RECOMMENDATIONS
# ========================================================

with gr.Tab(
    "Style Recommendations"
):

    recommendation_output = gr.Markdown(
        """
```

## Style Recommendations

Generate a look to receive
AI-powered styling explanations.
"""
)

```
    occasion_output = gr.Markdown(
        """
```

## Occasion Intelligence

Your recommended occasions will appear here.
"""
)

```
# ========================================================
# ACCESSORIES
# ========================================================

with gr.Tab(
    "Accessories and Shopping"
):

    accessories_output = gr.Markdown(
        """
```

## Complete the Look

Generate a look to receive accessory recommendations.
"""
)

```
    gr.Markdown(
        """
```

### Shopping Intelligence

Recommendations are intended as styling guidance.
Availability and pricing may vary.
"""
)

```
# ========================================================
# HISTORY
# ========================================================

with gr.Tab(
    "Try-On History"
):

    history_output = gr.Textbox(
        label="Saved Try-On History",
        lines=15,
        value=(
            "Click Refresh History "
            "to load saved looks."
        ),
    )

    refresh_history = gr.Button(
        "Refresh History"
    )

    refresh_history.click(
        fn=load_history,
        outputs=history_output,
    )

# ========================================================
# PIPELINE VISUALIZATION
# ========================================================

gr.Markdown(
    "## AI Fashion Intelligence Pipeline"
)

with gr.Row():

    with gr.Column():

        gr.HTML(
            """
```

<div class="pipeline">

<div class="pipeline-number">01</div>

<b>Upload</b>

<p>Person + Garment</p>

</div>
"""
            )

```
    with gr.Column():

        gr.HTML(
            """
```

<div class="pipeline">

<div class="pipeline-number">02</div>

<b>Validate</b>

<p>Computer Vision</p>

</div>
"""
            )

```
    with gr.Column():

        gr.HTML(
            """
```

<div class="pipeline">

<div class="pipeline-number">03</div>

<b>Analyze</b>

<p>Garment Intelligence</p>

</div>
"""
            )

```
    with gr.Column():

        gr.HTML(
            """
```

<div class="pipeline">

<div class="pipeline-number">04</div>

<b>Try-On</b>

<p>IDM-VTON</p>

</div>
"""
            )

```
    with gr.Column():

        gr.HTML(
            """
```

<div class="pipeline">

<div class="pipeline-number">05</div>

<b>Style</b>

<p>AI Recommendations</p>

</div>
"""
            )

```
# ========================================================
# GENERATE EVENT
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

gr.HTML(
    """
```

<div class="footer">

<b>AI Virtual Fashion Studio</b>

<br><br>

Machine Learning | Computer Vision | Deep Learning |
IDM-VTON | Image Processing | Gradio

<br><br>

Person + Garment -> Validation -> Preprocessing ->
Garment Intelligence -> Fashion Profile ->
Virtual Try-On -> Style Analysis -> Recommendations

</div>
"""
    )

# ============================================================

# APPLICATION ENTRY POINT

# ============================================================

if **name** == "**main**":

```
demo.launch(
    css=CUSTOM_CSS,
    server_name="127.0.0.1",
    server_port=7860,
    show_error=True,
)
```
