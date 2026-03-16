# CLAUDE.md — Nexus Fashion Generator

## Project Overview

A Streamlit-based web application that enables fashion designers to generate brand-styled clothing visuals from text descriptions. The system calls the fal.ai API to run FLUX.1-dev with fashion-specific LoRA adapters, returning high-quality garment images within seconds.

The immediate goal is a working demo for Professor Gene Wen (NYU Shanghai) that demonstrates prompt-driven brand-style clothing generation. Quality and speed matter more than feature completeness at this stage.

---

## Core User Flow

1. User selects a brand style preset (or types a custom style description)
2. User describes the garment in natural language
3. User clicks Generate
4. App calls fal.ai API with constructed prompt + LoRA config
5. Generated image appears in the UI
6. User can download the image or iterate with a new description

---

## Tech Stack

- **Frontend/Backend**: Streamlit (single-file app, `app.py`)
- **Image Generation API**: fal.ai (`fal-client` Python SDK)
- **Base Model**: `fal-ai/flux/dev` (FLUX.1-dev on fal.ai)
- **Primary LoRA**: `tryonlabs/FLUX.1-dev-LoRA-Outfit-Generator` (HuggingFace)
- **Environment**: Python 3.10+, runs on MacBook Air M4 or any machine with internet access
- **Config**: `.env` file for API keys (never hardcoded)

---

## Project Structure

```
nexus-fashion/
├── CLAUDE.md               # This file
├── README.md               # Setup instructions
├── .env                    # FAL_KEY=your_key (gitignored)
├── .gitignore
├── requirements.txt
├── app.py                  # Main Streamlit application
├── core/
│   ├── __init__.py
│   ├── generator.py        # fal.ai API call logic
│   ├── prompt_builder.py   # Prompt construction from user inputs
│   └── lora_config.py      # LoRA definitions and weight configs
├── presets/
│   └── brand_styles.py     # Brand style preset definitions
└── assets/
    └── placeholder.png     # Shown before first generation
```

---

## Module Specifications

### `core/generator.py`

Responsible for all fal.ai API interaction.

```python
# Key function signature
def generate_image(
    prompt: str,
    loras: list[dict],          # [{"path": "hf_repo/name", "scale": 0.8}]
    image_size: str = "portrait_4_3",
    num_inference_steps: int = 28,
    guidance_scale: float = 3.5,
    seed: int | None = None,
) -> str:                       # Returns image URL
```

- Uses `fal_client.run()` (synchronous, simpler for Streamlit)
- Model endpoint: `"fal-ai/flux/dev"`
- On API error: raise a descriptive exception with the fal.ai error message
- Log prompt and parameters to console for debugging

### `core/prompt_builder.py`

Constructs the final prompt string from UI inputs.

```python
def build_prompt(
    brand_style: str,       # e.g. "Chanel", "Lululemon", or custom text
    garment_description: str,  # User's free-text description
    style_modifiers: list[str] | None = None,
) -> str:
```

Prompt construction rules:
- Base template: `"{garment_description}, {brand_style} aesthetic, fashion editorial photography, studio lighting, high quality"`
- If brand_style is a known preset, append its specific style tokens (defined in `presets/brand_styles.py`)
- If garment_description is empty, raise ValueError
- Keep total prompt under 300 tokens

### `core/lora_config.py`

Defines available LoRA configurations.

```python
# Phase 1: Single LoRA
LORA_OUTFIT_GENERATOR = {
    "path": "tryonlabs/FLUX.1-dev-LoRA-Outfit-Generator",
    "scale": 0.85,
}

# Phase 2 (future): Dual LoRA stack
LORA_HIGH_END_FASHION = {
    "path": "XLabs-AI/flux-style-lora",  # placeholder, update when tested
    "scale": 0.6,
}

LORA_PRESETS = {
    "outfit_only": [LORA_OUTFIT_GENERATOR],
    "outfit_premium": [LORA_OUTFIT_GENERATOR, LORA_HIGH_END_FASHION],  # phase 2
}
```

### `presets/brand_styles.py`

Each brand preset has a trigger phrase and a list of style tokens that get appended to the prompt.

```python
BRAND_PRESETS = {
    "Chanel": {
        "style_tokens": [
            "tweed fabric", "collarless jacket", "gold chain trim",
            "monochrome palette", "haute couture", "Parisian elegance"
        ],
        "negative_prompt": "casual, streetwear, athleisure",
    },
    "Lululemon": {
        "style_tokens": [
            "technical athletic fabric", "compression paneling",
            "functional design", "matte finish", "minimalist"
        ],
        "negative_prompt": "formal, evening wear",
    },
    "Oscar de la Renta": {
        "style_tokens": [
            "floral embroidery", "structured silhouette", "feminine",
            "evening wear", "rich color", "luxury fabric"
        ],
        "negative_prompt": "casual, sporty",
    },
    "GAP": {
        "style_tokens": [
            "casual American style", "clean lines", "basic essentials",
            "accessible fashion", "versatile wardrobe"
        ],
        "negative_prompt": "formal, haute couture",
    },
    "Custom": None,  # User fills in style description manually
}
```

---

## `app.py` — UI Layout and Logic

### Layout (top to bottom)

```
[Header]
  Title: "Nexus Fashion Generator"
  Subtitle: "Brand-style clothing generation powered by FLUX"

[Sidebar]
  Brand Style
    - Selectbox: Chanel / Lululemon / Oscar de la Renta / GAP / Custom
    - If Custom: text_input for style description

  Generation Settings (collapsible expander, collapsed by default)
    - Steps slider: 20–50, default 28
    - Guidance scale slider: 1.0–5.0, default 3.5, step 0.5
    - Seed input: number_input, default empty (random)
    - Image size: selectbox [portrait_4_3, square, landscape_4_3]

[Main Area — Left Column, 60%]
  Garment Description
    - text_area: "Describe the garment...", height=120
    - Placeholder example: "A fitted blazer with structured shoulders, 
      single-button closure, and contrast stitching"
  
  [Generate Button] — primary style, full width

[Main Area — Right Column, 40%]
  Generated Image
    - st.image(), use_column_width=True
    - Before generation: show assets/placeholder.png with caption
    - After generation: show result with Download button
    - During generation: st.spinner("Generating...")

[Footer — below columns]
  Current prompt preview (collapsed expander)
    - Shows the exact prompt string being sent to the API
    - Useful for debugging and for Gene to see what's happening
```

### State Management

Use `st.session_state` for:
- `last_image_url`: URL of the most recently generated image
- `last_prompt`: full prompt string of last generation
- `generation_count`: integer counter, shown in sidebar as "X images generated"

### Error Handling in UI

- If FAL_KEY is not set: show `st.error("FAL_KEY not found in environment. Please add it to .env")`
- If API call fails: show `st.error(f"Generation failed: {error_message}")`, do not crash
- If garment description is empty: show `st.warning("Please describe the garment first")`

---

## Environment Setup

### `requirements.txt`
```
streamlit>=1.32.0
fal-client>=0.5.0
python-dotenv>=1.0.0
Pillow>=10.0.0
requests>=2.31.0
```

### `.env` format
```
FAL_KEY=your_fal_ai_api_key_here
```

### `README.md` must include
1. Prerequisites (Python 3.10+)
2. `pip install -r requirements.txt`
3. How to get a fal.ai API key (fal.ai → Settings → API Keys)
4. How to set up `.env`
5. `streamlit run app.py`

---

## fal.ai API Usage

### Authentication
```python
import os
import fal_client
os.environ["FAL_KEY"] = os.getenv("FAL_KEY")
```

### API Call Structure
```python
result = fal_client.run(
    "fal-ai/flux/dev",
    arguments={
        "prompt": prompt,
        "loras": loras,                    # list of {path, scale}
        "image_size": image_size,
        "num_inference_steps": steps,
        "guidance_scale": guidance_scale,
        "seed": seed,                      # omit key if None
        "enable_safety_checker": False,    # fashion content may trigger false positives
    }
)
image_url = result["images"][0]["url"]
```

Note: fal.ai returns `result["images"]` as a list. Always access index `[0]`.

---

## Prompt Engineering Guidelines

Good prompt structure for this use case:
```
{garment type and structure}, {color and material}, {brand aesthetic tokens}, 
fashion editorial photography, studio lighting, white background, 
full garment visible, high quality, detailed fabric texture
```

Bad patterns to avoid:
- Describing people/models (Gene said "we care about cloth not people")
- Vague style words without specifics ("nice", "beautiful", "good")
- Conflicting style signals ("casual Chanel", "formal Lululemon")

---

## Development Phases

### Phase 1 — Current (implement now)
- Single LoRA: `tryonlabs/FLUX.1-dev-LoRA-Outfit-Generator`
- 4 brand presets: Chanel, Lululemon, Oscar de la Renta, GAP
- Basic Streamlit UI as described above
- Working download button
- Prompt preview in footer

### Phase 2 — After demo feedback
- Add second aesthetic LoRA for premium brands
- Add image history (last 5 generations shown as thumbnails)
- Add "Edit this design" input for iterative refinement
- Consider FLUX.1-Fill for inpainting-based iteration

---

## Key Constraints and Non-Goals

**Constraints:**
- No user authentication (single-user demo tool)
- No database or persistent storage
- No image upload from user (text-to-image only in Phase 1)
- Must work without GPU (API-based)

**Non-goals for Phase 1:**
- Virtual try-on (putting garment on model image)
- Multi-garment generation
- Training custom LoRA
- Mobile responsiveness

---

## Testing Checklist

Before showing to Gene, verify:
- [ ] App starts with `streamlit run app.py` without errors
- [ ] Chanel preset generates a visually distinct result from Lululemon preset
- [ ] Custom brand input works
- [ ] Download button saves the image correctly
- [ ] Empty garment description shows warning (not crash)
- [ ] Invalid API key shows error (not crash)
- [ ] Prompt preview shows the actual string sent to API
- [ ] Generation takes under 30 seconds
