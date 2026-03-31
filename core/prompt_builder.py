from presets.brand_styles import BRAND_PRESETS


# Display mode prompt fragments
DISPLAY_MODES = {
    "product": {
        "label": "产品图 (Product Shot)",
        "suffixes": [
            "fashion design illustration, clean rendering",
            "uniform color palette",
            "light grey studio background",
            "full garment visible",
        ],
    },
    "on_model": {
        "label": "模特上身 (On Model)",
        "suffixes": [
            "worn by a fashion model, full body shot",
            "editorial lookbook photography, studio lighting",
            "natural pose, clean background",
            "high quality, detailed fabric texture",
        ],
    },
    "flat_sketch": {
        "label": "款式平面图 (Technical Flat)",
        "suffixes": [
            "fashion technical flat sketch, garment flat lay",
            "front view, clean line drawing",
            "white background, no model, no shadow",
            "apparel design blueprint, vector style illustration",
        ],
    },
}


def build_prompt(
    brand_style: str, # name of targeted brand: eg. Nike, lululemon etc.
    garment_description: str,
    style_modifiers: list[str] | None = None,
    display_mode: str = "product",
) -> str:
    if not garment_description or not garment_description.strip():
        raise ValueError("Garment description cannot be empty.")

    preset = BRAND_PRESETS.get(brand_style) # Find brand_style in BRAND_PRESETS

    if preset is not None and brand_style != "Custom":
        tokens = ", ".join(preset["style_tokens"])
        style_part = f"{brand_style} aesthetic, {tokens}"
    else:
        style_part = f"{brand_style} aesthetic" if brand_style else "fashion aesthetic"

    mode_config = DISPLAY_MODES.get(display_mode, DISPLAY_MODES["product"])

    parts = [
        style_part,
        garment_description.strip(),
        *mode_config["suffixes"],
    ]

    if style_modifiers:
        parts[1:1] = style_modifiers # insert modifiers between garment_description & style_part

    prompt = ", ".join(parts)

    # Rough token guard: ~4 chars per token, keep under 300 tokens (~1200 chars)
    if len(prompt) > 1200:
        prompt = prompt[:1197] + "..."

    return prompt


def get_negative_prompt(brand_style: str) -> str | None:
    preset = BRAND_PRESETS.get(brand_style)
    if preset and preset.get("negative_prompt"):
        return preset["negative_prompt"]
    return None
