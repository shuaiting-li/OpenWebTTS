import os
import uvicorn
import argparse
import threading
import time
import socket

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Import config first — it sets HF_HOME / TTS_HOME env vars and creates
# writable directories before any TTS module is imported.
import config
from functions.routes import router
from functions.openai_api import openai_api_router

# Point pytesseract at the resolved tesseract binary (bundled or system).
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = config.binary_path("tesseract")
except Exception:
    pass

# --- FastAPI Setup ---
app = FastAPI()
# Mount the writable audio_cache dir BEFORE the read-only static dir so the
# more specific path wins. The frontend still requests /static/audio_cache/...
app.mount("/static/audio_cache", StaticFiles(directory=config.AUDIO_CACHE_DIR), name="audio_cache")
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")

app.include_router(router)
app.include_router(openai_api_router)

# --- Main Execution ---
def _find_free_port(preferred_port: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", preferred_port))
            return preferred_port
        except OSError:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenWebTTS server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--app", action="store_true", help="Launch as a desktop app using a webview")
    parser.add_argument("--debug", action="store_true", help="Toggle various debug features")
    parser.add_argument("--device", default="cpu", help="Use specific device for inference with AI models")
    args = parser.parse_args()

    host = args.host
    port = _find_free_port(args.port)

    if args.device == 'cuda':
        config.DEVICE = 'cuda'

    if not args.app:
        print("Starting OpenWebTTS server...")
        print(f"Access the UI at http://{host}:{port}")
        uvicorn.run(app, host=host, port=port)
    else:
        try:
            import webview
        except Exception as e:
            print("pywebview is required for desktop mode. Install with: pip install pywebview")
            raise

        print("Starting OpenWebTTS in app mode...")
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)

        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()

        # Wait briefly for the server to start
        for _ in range(50):
            if getattr(server, "started", False):
                break
            time.sleep(0.1)

        url = f"http://{host}:{port}"
        print(f"Opening desktop window at {url}")

        server_debug = False

        if (args.debug == "true"):
            server_debug = True

        try:
            window = webview.create_window("OpenWebTTS", url,
            width=1280, height=720, resizable=True, text_select=True, fullscreen=False)
            window.icon = config.ICON_PATH

            webview.start(debug=server_debug, private_mode=False)
        finally:
            # Signal server to exit and wait a moment
            try:
                server.should_exit = True
            except Exception:
                pass
            time.sleep(0.2)
