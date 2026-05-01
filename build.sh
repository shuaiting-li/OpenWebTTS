#!/usr/bin/env bash
# Build a macOS .app bundle for OpenWebTTS.
#
# Output: dist/OpenWebTTS.app
#
# This is the no-Apple-Developer-account path: ad-hoc signed only, no
# notarization, no .dmg yet. End users running this on a machine other than
# the build machine will hit the Gatekeeper "unidentified developer" prompt
# and need to right-click → Open the first time. See INSTALL.md.
#
# When the project moves to a paid Apple Developer account, add:
#   - codesign --force --options runtime --entitlements entitlements.plist \
#       --sign "Developer ID Application: <NAME> (<TEAM>)" dist/OpenWebTTS.app
#   - xcrun notarytool submit ... --wait
#   - xcrun stapler staple dist/OpenWebTTS.app

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ ! -d venv ]; then
  echo "ERROR: venv not found. Create it with:" >&2
  echo "  uv venv && uv pip install -r requirements.txt pyinstaller" >&2
  exit 1
fi

echo "==> Building frontend assets (npm)"
npm install --silent
npm run build

echo "==> Running PyInstaller"
./venv/bin/pyinstaller OpenWebTTS.spec --noconfirm

echo "==> Ad-hoc signing"
codesign --force --deep --sign - dist/OpenWebTTS.app

echo "==> Verifying signature is internally consistent"
codesign --verify --deep --strict dist/OpenWebTTS.app
echo "    (spctl will reject this — that's expected for ad-hoc signing.)"

echo "==> Done: dist/OpenWebTTS.app"
echo "    Try: open dist/OpenWebTTS.app"
