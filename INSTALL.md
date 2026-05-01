# Installing OpenWebTTS on macOS

This is a personal-fork build, **not notarized by Apple**. macOS's Gatekeeper will warn the first time you open it. Once allowed, it works normally.

## First launch

1. Download `OpenWebTTS-mac.dmg` from the [releases page](https://github.com/shuaiting-li/OpenWebTTS/releases) (when published).
2. Open the `.dmg` and drag `OpenWebTTS.app` to `/Applications`.
3. **First time only:** right-click `OpenWebTTS.app` → **Open** → click **Open** in the dialog. (Double-clicking the first time will show "Apple cannot check it for malicious software" with no Open option — you must use right-click.)
4. After that, double-click works normally.

## Where your data lives

- Models, audio cache, user data: `~/Library/Application Support/OpenWebTTS/`
- The `.app` itself is read-only. Nothing is written inside the bundle.

## Uninstall

1. Drag `OpenWebTTS.app` to Trash.
2. Optionally remove your data: `~/Library/Application Support/OpenWebTTS/` (this also drops the cached model files, so re-installing will re-download them).

That's it — there's no installer that scatters files across the system.

## Building from source

If you want to build the `.app` yourself rather than download:

```sh
git clone https://github.com/shuaiting-li/OpenWebTTS.git
cd OpenWebTTS
git checkout packaging-macos

# Set up the Python env (uv is fastest; pip works too):
uv venv
uv pip install -r requirements.txt pyinstaller

# Build:
./build.sh
open dist/OpenWebTTS.app
```

You'll need Node.js (for `npm run build` of the frontend assets) and Homebrew binaries: `ffmpeg`, `tesseract`, `pdftoppm` (via `brew install ffmpeg tesseract poppler`).
