import os
import base64
from typing import Union
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()


def extract_garment_description(image_input: Union[str, bytes]) -> str:
    """
    Extract garment description from a sketch image using Qwen's vision API.

    Args:
        image_input: Either a file path (str) or raw image bytes

    Returns:
        Garment description extracted from the image
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
                            "text": """Describe this fashion technical flat in one concise paragraph.
Focus only on: garment type, silhouette, waist height, leg width,
pocket details, closure type, fabric texture, color.
Do not mention the illustration style.
Write as if describing a real garment for a product listing."""
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
                            return content_item.get("text", "")

        raise ValueError(f"Unexpected Qwen API response structure: {result}")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Qwen API request failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to extract description from sketch: {e}")
