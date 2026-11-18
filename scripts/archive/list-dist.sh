#!/bin/bash
set -u
B=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin
echo "=== dist/bin ==="
ls -la "$B" | head -60
echo
echo "=== chrome dir ==="
ls "$B/chrome" 2>/dev/null | head -10
echo
echo "=== defaults tree ==="
find "$B/defaults" -maxdepth 2 2>/dev/null | head -20
echo
echo "=== dirs sizes ==="
du -sh "$B"/chrome "$B"/defaults "$B"/dictionaries "$B"/res 2>/dev/null
echo
echo "=== app dir? ==="
ls -d "$B"/mobile 2>/dev/null; find "$B" -maxdepth 1 -type d | sed 's|.*/||' | tr '\n' ' '
