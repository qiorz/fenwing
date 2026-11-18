#!/bin/bash
# Fenwing — engine binaries installer (Linux / macOS / WSL)
#
# Usage: ./install.sh /path/to/fenwing/app
set -euo pipefail

APP="${1:?usage: install.sh <path-to-app>}"
HERE="$(cd "$(dirname "$0")" && pwd)"

[ -d "$APP/gecko" ] || { echo "not an app/ directory: $APP" >&2; exit 1; }

echo "[1/4] runtime libs -> app/gecko/libs/arm64-v8a"
mkdir -p "$APP/gecko/libs/arm64-v8a"
cp -f "$HERE"/gecko/libs/arm64-v8a/* "$APP/gecko/libs/arm64-v8a/"

echo "[2/4] NAPI link libs -> app/gecko/src/main/libs/arm64-v8a"
mkdir -p "$APP/gecko/src/main/libs/arm64-v8a"
cp -Rf "$HERE"/gecko/src/main/libs/arm64-v8a/* "$APP/gecko/src/main/libs/arm64-v8a/"
cp -f "$APP/gecko/libs/arm64-v8a/libxul.so" "$APP/gecko/src/main/libs/arm64-v8a/libxul.so"

echo "[3/4] GRE resources -> app/gecko/src/main/resources/rawfile/omni.ja"
cp -f "$HERE/gecko/src/main/resources/rawfile/omni.ja" "$APP/gecko/src/main/resources/rawfile/omni.ja"

echo "[4/4] done. Open app/ in DevEco Studio and build (configure signing first)."
