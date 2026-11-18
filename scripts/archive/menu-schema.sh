#!/bin/bash
set -u
F=/home/dev/ff/gecko/widget/openharmony/OHOSMenuBridge.cpp
echo "=== SerializeOne / item fields ==="
sed -n '395,520p' "$F"
echo "=== json envelope ==="
sed -n '700,760p' "$F"
