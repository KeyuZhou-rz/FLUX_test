from presets.brand_styles import BRAND_PRESETS


def build_prompt(
    brand_style: str, # name of targeted brand: eg. Nike, lululemon etc.
    garment_description: str, 
    style_modifiers: list[str] | None = None,
) -> str:
    if not garment_description or not garment_description.strip():
        raise ValueError("Garment description cannot be empty.")

    preset = BRAND_PRESETS.get(brand_style) # Find brand_style in BRAND_PRESETS

    if preset is not None and brand_style != "Custom":
        tokens = ", ".join(preset["style_tokens"])
        style_part = f"{brand_style} aesthetic, {tokens}"
    else:
        style_part = f"{brand_style} aesthetic" if brand_style else "fashion aesthetic"

    parts = [
        style_part,
        garment_description.strip(),
        "fashion design illustration, clean rendering",
        "uniform color palette",
        "light grey studio background",
        "full garment visible",
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
