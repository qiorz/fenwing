#!/bin/bash
# copy-mozjs-headers.sh — 解引用符号链接，把 dist/include 完整拷进 HSP
set -eu
SRC=/home/dev/ff/obj-js/dist/include
DST=/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/libs/arm64-v8a/include
rm -rf "$DST"
mkdir -p "$DST"
cp -aL "$SRC"/. "$DST"/
echo "files=$(find "$DST" -type f | wc -l) links=$(find "$DST" -type l | wc -l)"
ls -l "$DST/jsapi.h" "$DST/js/Conversions.h" "$DST/mozilla/Casting.h" "$DST/js-config.h" 2>/dev/null || true
du -sh "$DST" 2>/dev/null || true
