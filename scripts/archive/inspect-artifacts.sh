#!/bin/bash
set -u
B=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin
READELF=/opt/ohos-sdk/native/llvm/bin/llvm-readelf
echo "=== key artifacts ==="
ls -lh "$B"/libxul.so "$B"/libgeckoview.so "$B"/libgeckoxcomp.so 2>/dev/null || echo "some missing"
echo
echo "=== all .so in dist/bin ==="
ls -1 "$B"/*.so 2>/dev/null | sed 's|.*/||' | tr '\n' ' '
echo
echo "=== libxul DT_NEEDED ==="
$READELF -d "$B/libxul.so" 2>/dev/null | grep NEEDED || echo "no libxul"
echo "=== libgeckoview DT_NEEDED ==="
$READELF -d "$B/libgeckoview.so" 2>/dev/null | grep NEEDED || echo "no libgeckoview"
echo
echo "=== omni.ja / chrome files ==="
ls -1 "$B" 2>/dev/null | grep -E 'omni|\.ja|chrome|defaults|dictionaries' | head -10
echo "=== dist/bin entries count ==="
ls -1 "$B" 2>/dev/null | wc -l
mkdir -p /mnt/d/ff-ohos/artifacts/gecko
cp -f "$B"/libxul.so "$B"/libgeckoview.so /mnt/d/ff-ohos/artifacts/gecko/ 2>/dev/null
cp -f "$B"/omni.ja /mnt/d/ff-ohos/artifacts/gecko/ 2>/dev/null
echo "=== copied ==="
ls -lh /mnt/d/ff-ohos/artifacts/gecko/
