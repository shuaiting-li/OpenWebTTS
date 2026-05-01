# PyInstaller spec for OpenWebTTS macOS .app bundle.
#
# Build: pyinstaller OpenWebTTS.spec
# Sign : codesign --force --deep --sign - dist/OpenWebTTS.app
# Run  : open dist/OpenWebTTS.app
#
# This is the minimal viable spec — bundles the FastAPI app + pywebview
# wrapper + the Piper TTS engine. Other engines (Coqui, Kokoro, Whisper) are
# included via PyInstaller's auto-detection but not exercised by the smoke
# test; tighten or trim later as needed.

# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

ROOT = Path(SPECPATH)

# --- Bundled assets ---
datas = [
    (str(ROOT / 'static'), 'static'),
    (str(ROOT / 'templates'), 'templates'),
    (str(ROOT / 'maskable_icon_x128.png'), '.'),
    (str(ROOT / 'maskable_icon_x48.png'), '.'),
    (str(ROOT / 'maskable_icon_x512.png'), '.'),
]
# Piper ships its espeak-ng phoneme data inside the wheel; without it the
# Python API silently falls back to incorrect phonemization.
datas += collect_data_files('piper')

# --- Hidden imports ---
# FastAPI/uvicorn/Starlette use a lot of dynamic imports that PyInstaller
# misses. These cover the ones routes.py + uvicorn need at startup.
hiddenimports = [
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.loops.auto',
    'uvicorn.loops.asyncio',
    'uvicorn.loops.uvloop',
    'uvicorn.logging',
]
# Piper wraps onnxruntime; pull its providers in fully.
hiddenimports += collect_submodules('onnxruntime')
hiddenimports += collect_submodules('piper')

a = Analysis(
    ['app.py'],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # tkinter is unused by us and pulls in a hefty Tcl/Tk framework.
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OpenWebTTS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='OpenWebTTS',
)

app = BUNDLE(
    coll,
    name='OpenWebTTS.app',
    icon=None,  # add a .icns later via `iconutil` from maskable_icon_x512.png
    bundle_identifier='io.github.gyyyn.openwebtts',
    info_plist={
        'CFBundleName': 'OpenWebTTS',
        'CFBundleDisplayName': 'OpenWebTTS',
        'CFBundleShortVersionString': '0.1.0',
        'CFBundleVersion': '0.1.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '12.0',
        # Suppress the menu-bar-only-on-foreground default — we ARE foreground.
        'LSUIElement': False,
        # Required reasons (informational; only enforced by App Store).
        'NSHumanReadableCopyright': 'Open source TTS reader.',
    },
)
