"""
Hugging Face Spaces Entrypoint (Gradio & FastAPI Hybrid).
Provides compatibility with Hugging Face Free Tier Gradio SDK while serving the custom Sea Blue UI.
"""

import os

# Disable Gradio 6 SSR Node proxy so FastAPI/Uvicorn directly binds port 7860
os.environ["GRADIO_SSR_MODE"] = "False"

import gradio as gr
from main import app
from config import get_settings

# Create lightweight Gradio block for Hugging Face Spaces environment detection
with gr.Blocks(title="System One // Fitment Matcher") as demo:
    gr.HTML("<meta http-equiv='refresh' content='0; url=/'>")

# Mount Gradio onto our FastAPI application at /gradio
# Preserves root '/' serving our Sea Blue HTML interface and all '/api/*' REST endpoints
app = gr.mount_gradio_app(app, demo, path="/gradio", ssr_mode=False)

if __name__ == "__main__":
    import uvicorn
    app_settings = get_settings()
    uvicorn.run(
        app,
        host=app_settings.SERVER_HOST,
        port=app_settings.SERVER_PORT
    )
