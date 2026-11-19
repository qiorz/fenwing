#!/bin/bash
set -eu
L=/home/dev/ff/gecko/obj-hw/dist/bin/libxul.so
P=/mnt/d/ff-ohos/work/firefoxport/gecko/libs/arm64-v8a/libxul.so
B=/mnt/d/ff-ohos/artifacts/gecko/libxul-soft-phase0.so
ls -lh "$L"
echo "permission section count: $(readelf -S "$L" | grep -c permission || true)"
cp -f "$L" /mnt/d/ff-ohos/artifacts/gecko/libxul-hw-unstripped.so
/opt/ohos-sdk/native/llvm/bin/llvm-strip --strip-unneeded "$L"
ls -lh "$L"
cp -f "$P" "$B" 2>/dev/null || true
cp -f "$L" "$P"
ls -lh "$P"
