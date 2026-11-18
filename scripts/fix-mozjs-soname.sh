#!/bin/bash
# fix-mozjs-soname.sh — DT_NEEDED 是 libmozjs-142a1.so，HSP 里必须给这个名字
set -eu
LIBS2=/mnt/d/ff-ohos/work/firefoxport/gecko/libs/arm64-v8a
A=/mnt/d/ff-ohos/artifacts/mozjs
cp -f "$A/libmozjs.so" "$LIBS2/libmozjs-142a1.so"
rm -f "$LIBS2/libmozjs.so"
ls -lh "$LIBS2"
echo "--- SONAME check ---"
/opt/ohos-sdk/native/llvm/bin/llvm-readelf -d "$LIBS2/libmozjs-142a1.so" | grep SONAME
echo SONAME_FIX_DONE
