import os
import requests
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from core.generator import generate_image, generate_from_sketch
from core.prompt_builder import build_prompt, DISPLAY_MODES, build_kontext_prompt, KONTEXT_DISPLAY_MODES
from core.lora_config import LORA_PRESETS

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
if "sketch_image" not in st.session_state:
    st.session_state.sketch_image = None

# ── FAL_KEY check ─────────────────────────────────────────────────────────────
fal_key = os.getenv("FAL_KEY")
if not fal_key:
    st.error("FAL_KEY not found in environment. Please add it to .env")
    st.stop()
os.environ["FAL_KEY"] = fal_key

# ── Header ────────────────────────────────────────────────────────────────────
st.title("FLUX Fashion Generator")
st.caption("Sketch-to-image clothing generation powered by FLUX Kontext")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Sketch Upload")
    sketch_file = st.file_uploader(
        "Upload a sketch or technical flat",
        type=["png", "jpg", "jpeg"],
        help="Upload a garment sketch — FLUX Kontext will transform it into a realistic image"
    )

    if sketch_file:
        st.session_state.sketch_image = sketch_file.getvalue()
        st.image(sketch_file, caption="Uploaded sketch", use_column_width=True)
    else:
        st.session_state.sketch_image = None

    st.markdown("---")
    st.header("展示模式")

    # Use Kontext display modes when sketch is uploaded, otherwise standard modes
    has_sketch = st.session_state.sketch_image is not None
    if has_sketch:
        mode_source = KONTEXT_DISPLAY_MODES
    else:
        mode_source = DISPLAY_MODES

    display_mode_keys = list(mode_source.keys())
    display_mode_labels = [mode_source[k]["label"] for k in display_mode_keys]
    selected_display_label = st.radio(
        "选择展示模式",
        display_mode_labels,
        index=0,
    )
    selected_display_mode = display_mode_keys[display_mode_labels.index(selected_display_label)]

    st.markdown("---")
    st.metric("Images generated", st.session_state.generation_count)

    st.markdown("---")
    with st.expander("Generation Settings", expanded=False):
        steps = st.slider("Inference steps", 20, 50, 28)
        default_guidance = 2.5 if has_sketch else 3.5
        guidance = st.slider("Guidance scale", 1.0, 5.0, default_guidance, step=0.5)
        seed_input = st.number_input(
            "Seed (leave 0 for random)", min_value=0, max_value=2**32 - 1, value=0
        )
        if not has_sketch:
            image_size = st.selectbox(
                "Image size",
                ["portrait_4_3", "square", "landscape_4_3"],
                index=0,
            )
        else:
            image_size = "portrait_4_3"

    if has_sketch:
        st.info("Kontext 模式：直接理解草图生成效果图")
    else:
        st.info("文生图模式：通过文字描述生成服装图")

# ── Main area ─────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([0.6, 0.4])

with col_left:
    if has_sketch:
        st.subheader("Additional Description (Optional)")
        garment_desc = st.text_area(
            label="补充描述（可选）",
            value="",
            placeholder="可以补充草图中不明显的细节，如面料、颜色偏好等。留空则完全依赖草图。",
            height=120,
            label_visibility="collapsed",
        )
    else:
        st.subheader("Garment Description")
        garment_desc = st.text_area(
            label="Describe the garment",
            value="",
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
    seed = int(seed_input) if seed_input and seed_input != 0 else None

    if has_sketch:
        # Kontext mode: sketch-to-image
        prompt = build_kontext_prompt(
            display_mode=selected_display_mode,
            extra_description=garment_desc,
        )
        st.session_state.last_prompt = prompt

        with col_right:
            with st.spinner("Generating with Kontext..."):
                try:
                    url = generate_from_sketch(
                        prompt=prompt,
                        sketch_image=st.session_state.sketch_image,
                        num_inference_steps=steps,
                        guidance_scale=guidance,
                        seed=seed,
                    )
                    st.session_state.last_image_url = url
                    st.session_state.generation_count += 1
                    image_placeholder.image(url, use_container_width=True)

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
    else:
        # Text-to-image mode
        if not garment_desc or not garment_desc.strip():
            st.warning("Please describe the garment first.")
        else:
            try:
                prompt = build_prompt(
                    garment_description=garment_desc,
                    display_mode=selected_display_mode,
                )
            except ValueError as e:
                st.warning(str(e))
                st.stop()

            st.session_state.last_prompt = prompt
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
