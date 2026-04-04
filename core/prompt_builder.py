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
    garment_description: str,
    display_mode: str = "product",
    style_modifiers: list[str] | None = None,
) -> str:
    """
    Build FLUX prompt from garment description and display mode.

    Args:
        garment_description: Detailed garment description or extracted features
        display_mode: Rendering style (product, on_model, flat_sketch)
        style_modifiers: Optional style modifiers to insert

    Returns:
        Complete prompt string for FLUX generation
    """
    if not garment_description or not garment_description.strip():
        raise ValueError("Garment description cannot be empty.")

    mode_config = DISPLAY_MODES.get(display_mode, DISPLAY_MODES["product"])

    parts = [
        garment_description.strip(),
        *mode_config["suffixes"],
    ]

    if style_modifiers:
        parts[1:1] = style_modifiers

    prompt = ", ".join(parts)

    # Rough token guard: ~4 chars per token, keep under 300 tokens (~1200 chars)
    if len(prompt) > 1200:
        prompt = prompt[:1197] + "..."

    return prompt


# ── Kontext mode (sketch-to-image) ───────────────────────────────────────────

KONTEXT_DISPLAY_MODES = {
    "product": {
        "label": "产品图 (Product Shot)",
        "instruction": (
            "Transform this fashion sketch into a realistic product photograph "
            "of the garment. Render it as a high-quality studio product shot "
            "with light grey background, realistic fabric texture and natural lighting. "
            "Keep the exact design, structure and color from the sketch."
        ),
    },
    "on_model": {
        "label": "模特上身 (On Model)",
        "instruction": (
            "Transform this fashion sketch into a realistic editorial photograph "
            "of the garment worn by a fashion model. Full body shot, studio lighting, "
            "natural pose, clean background, detailed fabric texture. "
            "Keep the exact design, structure and color from the sketch."
        ),
    },
    "flat_sketch": {
        "label": "款式平面图 (Technical Flat)",
        "instruction": (
            "Transform this into a clean fashion technical flat drawing. "
            "Front view, precise line work, white background, no model, no shadow. "
            "Apparel design blueprint style. Keep the exact design and structure."
        ),
    },
}


def build_kontext_prompt(
    display_mode: str = "product",
    extra_description: str = "",
) -> str:
    """Build a Kontext transformation prompt for sketch-to-image."""
    mode_config = KONTEXT_DISPLAY_MODES.get(display_mode, KONTEXT_DISPLAY_MODES["product"])
    prompt = mode_config["instruction"]

    if extra_description and extra_description.strip():
        prompt += f" Additional details: {extra_description.strip()}"

    if len(prompt) > 1200:
        prompt = prompt[:1197] + "..."

    return prompt
