# Changelog — v1.0 (Phase 1 Initial Release)

## Summary

First complete working implementation of Nexus Fashion Generator.
Covers all Phase 1 requirements from CLAUDE.md.

---

## New Files

| File | Description |
|---|---|
| `app.py` | Main Streamlit application |
| `core/generator.py` | fal.ai API wrapper (`fal_client.run`) |
| `core/prompt_builder.py` | Prompt construction with brand token injection |
| `core/lora_config.py` | LoRA definitions (outfit generator + future premium) |
| `presets/brand_styles.py` | 4 brand presets + Custom |
| `assets/placeholder.png` | Shown before first generation |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Excludes `.env`, caches, build artifacts |
| `README.md` | Setup guide |

---

## Features Implemented

### UI
- Page layout: sidebar (brand + settings) + two-column main area
- Brand selector: Chanel, Lululemon, Oscar de la Renta, GAP, Custom
- Custom brand: free-text style description input
- Generation settings (collapsible): steps, guidance scale, seed, image size
- Garment description textarea with placeholder example
- Primary "Generate" button (full width)
- Image display with `st.spinner` during generation
- Download button (saves PNG with incrementing filename)
- Prompt preview in collapsible footer expander
- Generation counter in sidebar

### Core Logic
- `build_prompt()`: appends brand style tokens, enforces ~300-token limit
- `get_negative_prompt()`: returns per-brand negative prompt string
- `generate_image()`: calls `fal-ai/flux/dev` with LoRA config, returns image URL
- Console logging of prompt + parameters for debugging

### Error Handling
- Missing `FAL_KEY`: `st.error` + `st.stop()`
- Empty garment description: `st.warning`
- API failure: `st.error` with error message, no crash

---

## Testing Checklist Status

- [x] App starts with `streamlit run app.py` without errors
- [x] Brand presets inject distinct style tokens per brand
- [x] Custom brand input wired through to prompt
- [x] Download button saves PNG
- [x] Empty description shows warning (not crash)
- [x] Missing API key shows error (not crash)
- [x] Prompt preview shows actual string sent to API
- [ ] End-to-end generation under 30s — requires live API key to verify

---

## Known Limitations (Phase 2)

- No image history / thumbnail strip
- No iterative "edit this design" input
- Single LoRA only (dual LoRA stack defined but not activated)
- No mobile responsive layout
