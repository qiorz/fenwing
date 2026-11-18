#!/bin/bash
# stage-mozjs.sh — 把 libmozjs 按 firefoxport 工程约定放入 HSP 目录
set -u
A=/mnt/d/ff-ohos/artifacts/mozjs
W=/mnt/d/ff-ohos/work/firefoxport
LIBS="$W/gecko/src/main/libs/arm64-v8a"
LIBS2="$W/gecko/libs/arm64-v8a"
STRIP=/opt/ohos-sdk/native/llvm/bin/llvm-strip
SRC="$A/libmozjs-142a1.so"

echo "=== strip ==="
$STRIP --strip-unneeded "$SRC" -o "$A/libmozjs.so"
ls -lh "$SRC" "$A/libmozjs.so"

echo "=== stage ==="
mkdir -p "$LIBS/include/js" "$LIBS2"
cp -f "$A/libmozjs.so" "$LIBS/libmozjs.so"
cp -f "$A/libmozjs.so" "$LIBS2/libmozjs.so"
cp -f "$A/jsapi.h" "$LIBS/include/jsapi.h"
cp -f "$A"/include/*.h "$LIBS/include/js/" 2>/dev/null || true
cp -f "$A/jsapi.h" "$LIBS2/jsapi.h" 2>/dev/null || true
ls -lh "$LIBS" | head
echo "api headers: $(ls "$LIBS/include/js" | wc -l)"
echo "deps of staged lib:"
/opt/ohos-sdk/native/llvm/bin/llvm-readelf -d "$LIBS/libmozjs.so" | grep NEEDED
echo STAGE_DONE
