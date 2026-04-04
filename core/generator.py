import fal_client


_SIZE_MAP = {
    "portrait_4_3":   {"width": 1024, "height": 1280},
    "square":         {"width": 1024, "height": 1024},
    "landscape_4_3":  {"width": 1280, "height": 1024},
}


def _upload_image(image_bytes: bytes) -> str:
    """Upload image bytes to fal storage and return a URL."""
    return fal_client.upload(image_bytes, content_type="image/png")


def generate_from_sketch(
    prompt: str,
    sketch_image: bytes,
    num_inference_steps: int = 28,
    guidance_scale: float = 2.5,
    seed: int | None = None,
) -> str:
    """Generate a realistic garment image from a sketch using FLUX Kontext/dev."""
    sketch_url = _upload_image(sketch_image)

    print(f"[generator:kontext] prompt: {prompt}")
    print(f"[generator:kontext] sketch uploaded, steps={num_inference_steps}, "
          f"guidance={guidance_scale}, seed={seed}")

    arguments = {
        "prompt": prompt,
        "image_url": sketch_url,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "enable_safety_checker": False,
        "output_format": "png",
    }

    if seed is not None:
        arguments["seed"] = seed

    try:
        result = fal_client.run("fal-ai/flux-kontext/dev", arguments=arguments)
    except Exception as e:
        raise RuntimeError(f"fal.ai Kontext API error: {e}") from e

    images = result.get("images", [])
    if not images:
        raise RuntimeError("fal.ai Kontext returned no images.")

    image_info = images[0]
    print(f"[generator:kontext] result size: {image_info.get('width')}x{image_info.get('height')}")
    return image_info["url"]


def generate_image(
    prompt: str,
    loras: list[dict],
    image_size: str | dict | None = None,
    num_inference_steps: int = 28,
    guidance_scale: float = 3.5,
    seed: int | None = None,
) -> str:
    """Generate a garment image from text using FLUX general + LoRA."""
    if image_size is None:
        image_size = {"width": 1024, "height": 1280}
    elif isinstance(image_size, str):
        image_size = _SIZE_MAP.get(image_size, {"width": 1024, "height": 1280})

    print(f"[generator:text] prompt: {prompt}")
    print(f"[generator:text] loras: {loras}")
    print(f"[generator:text] image_size={image_size}, steps={num_inference_steps}, "
          f"guidance={guidance_scale}, seed={seed}")

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

    try:
        result = fal_client.run("fal-ai/flux-general", arguments=arguments)
    except Exception as e:
        raise RuntimeError(f"fal.ai API error: {e}") from e

    images = result.get("images", [])
    if not images:
        raise RuntimeError("fal.ai returned no images.")

    image_info = images[0]
    print(f"[generator:text] actual size: {image_info.get('width')}x{image_info.get('height')}")
    return image_info["url"]
