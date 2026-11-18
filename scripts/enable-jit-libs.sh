#!/bin/bash
# enable-jit-libs.sh — 把 ports/ohos/permission.json 注入 libxul.so 的 .permission 段
# 用法: enable-jit-libs.sh <输入 libxul.so> <输出 libxul.so>
set -eu
NDK=/opt/ohos-sdk/native
PERM=/home/dev/ff/gecko/ports/ohos/permission.json
SRC=${1:?input libxul}
OUT=${2:?output libxul}
TMP=$(mktemp /tmp/libxul-perm-XXXX.so)
cp -f "$SRC" "$TMP"
$NDK/llvm/bin/llvm-objcopy --add-section ".permission=$PERM" \
  --set-section-flags .permission=readonly "$TMP" "$OUT"
echo "injected .permission into $OUT"
$NDK/llvm/bin/llvm-readelf -S "$OUT" | grep -i permission || echo "WARN: section missing"
$NDK/llvm/bin/llvm-readelf -x .permission "$OUT" | head -6
rm -f "$TMP"
