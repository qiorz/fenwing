#!/bin/bash
# stage-mozjs-headers.sh — 把 dist/include 全量拷进 HSP 的 include 目录（jsapi.h/js/mozilla 等）
set -eu
SRC=/home/dev/ff/obj-js/dist/include
DST=/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/libs/arm64-v8a/include
mkdir -p "$DST"
cp -r "$SRC"/. "$DST"/
echo "top-level entries: $(ls "$DST" | wc -l)"
for f in jsapi.h js/Conversions.h mozilla/Casting.h js/RequiredDefines.h; do
  if [ -f "$DST/$f" ]; then echo "OK   $f"; else echo "MISS $f"; fi
done
du -sh "$DST"
