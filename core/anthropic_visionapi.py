import os
import anthropic
import base64
from typing import Union
from dotenv import load_dotenv

load_dotenv()


def extract_garment_description(image_input: Union[str, bytes]) -> str:
    """
    Extract garment description from a sketch image using Claude's vision API.

    Args:
        image_input: Either a file path (str) or raw image bytes

    Returns:
        Garment description extracted from the image
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env file")

    client = anthropic.Anthropic(api_key=api_key)

    # Handle both file path and bytes input
    if isinstance(image_input, str):
        with open(image_input, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
    else:
        image_data = base64.b64encode(image_input).decode("utf-8")
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data,
                    },
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
        }]
    )
    return message.content[0].text