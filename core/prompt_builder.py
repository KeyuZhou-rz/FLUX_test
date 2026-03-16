from presets.brand_styles import BRAND_PRESETS


def build_prompt(
    brand_style: str,
    garment_description: str,
    style_modifiers: list[str] | None = None,
) -> str:
    if not garment_description or not garment_description.strip():
        raise ValueError("Garment description cannot be empty.")

    preset = BRAND_PRESETS.get(brand_style)

    if preset is not None and brand_style != "Custom":
        tokens = ", ".join(preset["style_tokens"])
        style_part = f"{brand_style} aesthetic, {tokens}"
    else:
        style_part = f"{brand_style} aesthetic" if brand_style else "fashion aesthetic"

    parts = [
        garment_description.strip(),
        style_part,
        "fashion editorial photography",
        "studio lighting",
        "white background",
        "full garment visible",
        "high quality",
        "detailed fabric texture",
    ]

    if style_modifiers:
        parts[1:1] = style_modifiers

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
