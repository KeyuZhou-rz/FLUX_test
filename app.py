import os
import io
import requests
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from core.generator import generate_image
from core.prompt_builder import build_prompt, get_negative_prompt
from core.lora_config import LORA_PRESETS
from presets.brand_styles import BRAND_PRESETS

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FLUX Fashion Generator",
    page_icon="✦",
    layout="wide",
)

# ── Session state init ────────────────────────────────────────────────────────
if "last_image_url" not in st.session_state:
    st.session_state.last_image_url = None
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""
if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0

# ── FAL_KEY check ─────────────────────────────────────────────────────────────
fal_key = os.getenv("FAL_KEY")
if not fal_key:
    st.error("FAL_KEY not found in environment. Please add it to .env")
    st.stop()
os.environ["FAL_KEY"] = fal_key

# ── Header ────────────────────────────────────────────────────────────────────
st.title("FLUX Fashion Generator")
st.caption("Brand-style clothing generation powered by FLUX")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Brand Style")

    brand_names = list(BRAND_PRESETS.keys())
    selected_brand = st.selectbox("Select brand preset", brand_names, index=0)

    custom_style = ""
    if selected_brand == "Custom":
        custom_style = st.text_input(
            "Custom style description",
            placeholder="e.g. minimalist Scandinavian streetwear",
        )

    st.markdown("---")
    st.metric("Images generated", st.session_state.generation_count)

    st.markdown("---")
    with st.expander("Generation Settings", expanded=False):
        steps = st.slider("Inference steps", 20, 50, 28)
        guidance = st.slider("Guidance scale", 1.0, 5.0, 3.5, step=0.5)
        seed_input = st.number_input(
            "Seed (leave 0 for random)", min_value=0, max_value=2**32 - 1, value=0
        )
        image_size = st.selectbox(
            "Image size",
            ["portrait_4_3", "square", "landscape_4_3"],
            index=0,
        )

# ── Main area ─────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([0.6, 0.4])

with col_left:
    st.subheader("Garment Description")
    garment_desc = st.text_area(
        label="Describe the garment",
        placeholder=(
            "A fitted blazer with structured shoulders, "
            "single-button closure, and contrast stitching"
        ),
        height=120,
        label_visibility="collapsed",
    )

    generate_clicked = st.button("Generate", type="primary", use_container_width=True)

with col_right:
    st.subheader("Generated Image")
    image_placeholder = st.empty()
    download_placeholder = st.empty()

    if st.session_state.last_image_url:
        image_placeholder.image(
            st.session_state.last_image_url, use_container_width=True
        )
    else:
        placeholder_path = Path("assets/placeholder.png")
        if placeholder_path.exists():
            image_placeholder.image(
                str(placeholder_path),
                caption="Your generated image will appear here",
                use_container_width=True,
            )
        else:
            image_placeholder.info("Your generated image will appear here.")

# ── Generation logic ──────────────────────────────────────────────────────────
if generate_clicked:
    if not garment_desc or not garment_desc.strip():
        st.warning("Please describe the garment first.")
    else:
        brand_style_value = custom_style if selected_brand == "Custom" else selected_brand

        try:
            prompt = build_prompt(
                brand_style=brand_style_value,
                garment_description=garment_desc,
            )
        except ValueError as e:
            st.warning(str(e))
            st.stop()

        st.session_state.last_prompt = prompt
        seed = int(seed_input) if seed_input and seed_input != 0 else None
        loras = LORA_PRESETS["outfit_only"]

        with col_right:
            with st.spinner("Generating..."):
                try:
                    url = generate_image(
                        prompt=prompt,
                        loras=loras,
                        image_size=image_size,
                        num_inference_steps=steps,
                        guidance_scale=guidance,
                        seed=seed,
                    )
                    st.session_state.last_image_url = url
                    st.session_state.generation_count += 1
                    image_placeholder.image(url, use_container_width=True)

                    # Download button
                    img_bytes = requests.get(url, timeout=30).content
                    download_placeholder.download_button(
                        label="Download Image",
                        data=img_bytes,
                        file_name=f"nexus_fashion_{st.session_state.generation_count}.png",
                        mime="image/png",
                        use_container_width=True,
                    )
                except RuntimeError as e:
                    st.error(f"Generation failed: {e}")

# ── Footer: prompt preview ────────────────────────────────────────────────────
st.markdown("---")
with st.expander("Prompt Preview", expanded=False):
    if st.session_state.last_prompt:
        st.code(st.session_state.last_prompt, language=None)
    else:
        st.caption("No prompt generated yet.")
