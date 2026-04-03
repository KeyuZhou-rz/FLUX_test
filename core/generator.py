import os
import base64
import fal_client
from typing import Union

_SIZE_MAP = {
    "portrait_4_3":   {"width": 1024, "height": 1280},
    "square":         {"width": 1024, "height": 1024},
    "landscape_4_3":  {"width": 1280, "height": 1024},
}


def _bytes_to_data_url(image_bytes: bytes) -> str:
    """Convert image bytes to base64 data URL."""
    b64_str = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


def generate_image(
    prompt: str,
    loras: list[dict],
    image_size: str | dict | None = None,
    num_inference_steps: int = 28,
    guidance_scale: float = 3.5,
    seed: int | None = None,
    sketch_image: Union[bytes, None] = None,
) -> str:
    if image_size is None:
        image_size = {"width": 1024, "height": 1280}
    elif isinstance(image_size, str):
        image_size = _SIZE_MAP.get(image_size, {"width": 1024, "height": 1280})

    print(f"[generator] prompt: {prompt}")
    print(f"[generator] loras: {loras}")
    print(f"[generator] image_size={image_size}, steps={num_inference_steps}, "
          f"guidance={guidance_scale}, seed={seed}")
    if sketch_image:
        print(f"[generator] sketch_image provided: {len(sketch_image)} bytes")

    arguments = {
        "prompt": prompt,
        "loras": loras,
        "image_size": image_size,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "enable_safety_checker": False,
    }

    if seed is not None:
        arguments["seed"] = seed

    # Add ControlNet if sketch image is provided
    if sketch_image:
        sketch_url = _bytes_to_data_url(sketch_image)
        arguments["controlnets"] = [{
            "path": "InstantX/FLUX.1-dev-Controlnet-Canny",
            "control_image_url": sketch_url,
            "scale": 0.7,
        }]

    try:
        result = fal_client.run(
            "fal-ai/flux-general",
            arguments=arguments,
        )
    except Exception as e:
        raise RuntimeError(f"fal.ai API error: {e}") from e

    images = result.get("images", [])
    if not images:
        raise RuntimeError("fal.ai returned no images.")

    image_info = result["images"][0]
    print(f"[generator] actual size: {image_info.get('width')}x{image_info.get('height')}")

    return image_info["url"]
