import os
import shutil
import sys
from fastapi.templating import Jinja2Templates


def _default_data_dir() -> str:
    """Platform-appropriate writable directory for user data and models."""
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/OpenWebTTS")
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "OpenWebTTS")
    return os.path.join(
        os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"),
        "OpenWebTTS",
    )


def _resource_dir() -> str:
    """Read-only directory containing bundled assets (static, templates, icons).

    Under PyInstaller this is sys._MEIPASS; otherwise it's the directory
    holding this file (the repo root in dev).
    """
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.dirname(os.path.abspath(__file__))


def binary_path(name: str) -> str:
    """Resolve an executable: bundled <RESOURCE_DIR>/bin, then sys.executable's dir
    (handles venv-without-activate), then PATH."""
    if getattr(sys, "frozen", False):
        bundled = os.path.join(RESOURCE_DIR, "bin", name)
        if os.path.exists(bundled):
            return bundled
    py_bin_dir = os.path.dirname(os.path.abspath(sys.executable))
    candidate = os.path.join(py_bin_dir, name)
    if os.path.exists(candidate) and os.access(candidate, os.X_OK):
        return candidate
    return shutil.which(name) or name


# --- Roots ---
DATA_DIR = os.environ.get("OPENWEBTTS_DATA_DIR") or _default_data_dir()
RESOURCE_DIR = _resource_dir()

# --- Read-only paths (under RESOURCE_DIR) ---
STATIC_DIR = os.path.join(RESOURCE_DIR, "static")
TEMPLATES_DIR = os.path.join(RESOURCE_DIR, "templates")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
ICON_PATH = os.path.join(RESOURCE_DIR, "maskable_icon_x128.png")

# --- Writable paths (under DATA_DIR) ---
MODELS_DIR = os.path.join(DATA_DIR, "models")
COQUI_DIR = os.path.join(MODELS_DIR, "coqui")
PIPER_DIR = os.path.join(MODELS_DIR, "piper")
KOKORO_DIR = os.path.join(MODELS_DIR, "kokoro")
AUDIO_CACHE_DIR = os.path.join(DATA_DIR, "audio_cache")
USERS_DIR = os.path.join(DATA_DIR, "users")
HF_CACHE_DIR = os.path.join(DATA_DIR, "hf_cache")

# Ensure writable dirs exist on import.
for _d in (DATA_DIR, MODELS_DIR, COQUI_DIR, PIPER_DIR, KOKORO_DIR, AUDIO_CACHE_DIR, USERS_DIR, HF_CACHE_DIR):
    os.makedirs(_d, exist_ok=True)

# Route Hugging Face / TTS caches into DATA_DIR so Coqui & friends don't
# write to ~/.cache. Must be set before any HF / TTS module import.
os.environ.setdefault("HF_HOME", HF_CACHE_DIR)
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", HF_CACHE_DIR)
os.environ.setdefault("TRANSFORMERS_CACHE", HF_CACHE_DIR)
os.environ.setdefault("TTS_HOME", HF_CACHE_DIR)

DEVICE = 'cpu'


def set_device(s):
    global DEVICE
    DEVICE = s


# --- Templates ---
templates = Jinja2Templates(directory=TEMPLATES_DIR)
