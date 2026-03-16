# Nexus Fashion Generator

Brand-style clothing generation powered by FLUX.1-dev + fal.ai.

## Prerequisites

- Python 3.10+
- A fal.ai account and API key

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a fal.ai API key

1. Go to [fal.ai](https://fal.ai)
2. Sign in → Settings → API Keys
3. Create a new key and copy it

### 3. Configure environment

Create a `.env` file in the project root:

```
FAL_KEY=your_fal_ai_api_key_here
```

### 4. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Usage

1. Select a brand style preset from the sidebar (Chanel, Lululemon, Oscar de la Renta, GAP, or Custom)
2. Describe the garment in the text area
3. Click **Generate**
4. Download the result with the Download button

## Project Structure

```
├── app.py                  # Main Streamlit application
├── core/
│   ├── generator.py        # fal.ai API call logic
│   ├── prompt_builder.py   # Prompt construction
│   └── lora_config.py      # LoRA configurations
├── presets/
│   └── brand_styles.py     # Brand style presets
└── assets/
    └── placeholder.png
```
