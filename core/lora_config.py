LORA_OUTFIT_GENERATOR = {
    "path": "tryonlabs/FLUX.1-dev-LoRA-Outfit-Generator",
    "scale": 0.85,
}

LORA_HIGH_END_FASHION = {
    "path": "XLabs-AI/flux-style-lora",  # placeholder, update when tested
    "scale": 0.6,
}

LORA_PRESETS = {
    "outfit_only": [LORA_OUTFIT_GENERATOR],
    "outfit_premium": [LORA_OUTFIT_GENERATOR, LORA_HIGH_END_FASHION],  # phase 2
}
