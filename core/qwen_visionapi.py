import os
import base64
import json
from typing import Union, Dict
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()


def extract_garment_description(image_input: Union[str, bytes]) -> Dict[str, str]:
    """
    Extract structured garment features from a sketch image using Qwen's vision API.

    Args:
        image_input: Either a file path (str) or raw image bytes

    Returns:
        Dict with keys: silhouette, color, fabric, details, mood
    """
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        raise ValueError("QWEN_API_KEY not found in .env file")

    # Handle both file path and bytes input
    if isinstance(image_input, str):
        with open(image_input, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
    else:
        image_data = base64.b64encode(image_input).decode("utf-8")

    # Prepare request to Qwen API
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "qwen-vl-plus",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": f"data:image/png;base64,{image_data}",
                        },
                        {
                            "type": "text",
                            "text": """This is a hand-drawn fashion sketch. Analyze the DESIGN INTENT of this garment, NOT the drawing technique.

IMPORTANT: Ignore all sketch rendering artifacts such as crosshatching, diagonal shading lines, pencil strokes, hatching patterns, or stippling. These are drawing techniques, NOT fabric textures. Describe the intended real-world fabric and texture instead.

For each dimension, provide 2-5 English phrases separated by commas:

1. SILHOUETTE: Length, sleeve length, cut, shoulder line, fit
2. COLOR: Intended real-world color (infer from shading density and context, not pencil color)
3. FABRIC: Intended real-world material and texture (e.g. cotton, silk, wool, denim — NOT crosshatch, hatching, or pencil strokes)
4. DETAILS: Collar type, placket, paneling, stitching, decorative elements
5. MOOD: 2-3 style keywords

Output ONLY valid JSON, no markdown formatting, no code block markers:
{"silhouette": "...", "color": "...", "fabric": "...", "details": "...", "mood": "..."}"""
                        }
                    ],
                }
            ]
        },
        "parameters": {
            "max_output_tokens": 300,
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()

        # Extract text from Qwen response
        if "output" in result and "choices" in result["output"]:
            choices = result["output"]["choices"]
            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                if "content" in message and len(message["content"]) > 0:
                    for content_item in message["content"]:
                        if isinstance(content_item, dict) and "text" in content_item:
                            text = content_item.get("text", "").strip()

                            # Remove markdown code block markers if present
                            if text.startswith("```json"):
                                text = text.replace("```json", "", 1).strip()
                            if text.startswith("```"):
                                text = text.replace("```", "", 1).strip()
                            if text.endswith("```"):
                                text = text[:-3].strip()

                            # Parse JSON
                            try:
                                return json.loads(text)
                            except json.JSONDecodeError as e:
                                raise ValueError(f"Failed to parse Qwen response as JSON: {text}\nError: {e}")

        raise ValueError(f"Unexpected Qwen API response structure: {result}")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Qwen API request failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to extract description from sketch: {e}")


def build_flux_prompt(
    garment_features: Dict[str, str],
    display_mode: str = "product"
) -> str:
    """
    Assemble FLUX prompt from extracted garment features.

    Args:
        garment_features: Dict from extract_garment_description with keys:
                         silhouette, color, fabric, details, mood
        display_mode: Rendering style (product, on_model, flat_sketch)

    Returns:
        Complete prompt string optimized for FLUX generation
    """
    from core.prompt_builder import DISPLAY_MODES

    # Assemble garment description: silhouette > color > details > fabric > mood (priority order)
    garment_desc = ", ".join([
        garment_features.get("silhouette", ""),
        garment_features.get("color", ""),
        garment_features.get("details", ""),
        garment_features.get("fabric", ""),
        garment_features.get("mood", ""),
    ])

    # Remove empty segments
    garment_desc = ", ".join([seg for seg in garment_desc.split(", ") if seg])

    mode_config = DISPLAY_MODES.get(display_mode, DISPLAY_MODES["product"])
    mode_suffix = ", ".join(mode_config["suffixes"])

    prompt = f"{garment_desc}, {mode_suffix}"

    # Token length optimization: rough estimate (English ~1 word ≈ 1.3 tokens)
    word_count = len(prompt.split())
    if word_count > 65:
        # Remove fabric and mood (lowest priority) if too long
        garment_desc = ", ".join([
            garment_features.get("silhouette", ""),
            garment_features.get("color", ""),
            garment_features.get("details", ""),
        ])
        garment_desc = ", ".join([seg for seg in garment_desc.split(", ") if seg])
        prompt = f"{garment_desc}, {mode_suffix}"

    return prompt
