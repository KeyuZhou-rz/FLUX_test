import os
import fal_client


def generate_image(
    prompt: str,
    loras: list[dict],
    image_size: str = "portrait_4_3",
    num_inference_steps: int = 28,
    guidance_scale: float = 3.5,
    seed: int | None = None,
) -> str:
    print(f"[generator] prompt: {prompt}")
    print(f"[generator] loras: {loras}")
    print(f"[generator] image_size={image_size}, steps={num_inference_steps}, "
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
        result = fal_client.run("fal-ai/flux/dev", arguments=arguments)
    except Exception as e:
        raise RuntimeError(f"fal.ai API error: {e}") from e

    images = result.get("images", [])
    if not images:
        raise RuntimeError("fal.ai returned no images.")

    return images[0]["url"]
