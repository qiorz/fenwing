#!/bin/bash
# build-omni.sh — 从 dist/bin 生成 omni.ja（STORED，便于 mmap）并放进 gecko HSP rawfile
set -eu
B=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin
W=/mnt/d/ff-ohos/work/firefoxport
OUT=/tmp/omni.ja
RAW=$W/gecko/src/main/resources/rawfile

rm -f "$OUT"
cd "$B"
set +e
zip -0 -r -X "$OUT" \
  chrome defaults components modules res actors hyphenation localization dictionaries \
  platform.ini chrome.manifest greprefs.js application.ini 2>&1 | tail -3
rc=$?
set -e
if [ $rc -ne 0 ] || [ ! -f "$OUT" ]; then
  echo "zip failed rc=$rc"
  exit 1
fi
mkdir -p "$RAW"
cp -f "$OUT" "$RAW/omni.ja"
ls -lh "$RAW/omni.ja"
echo "entries: $(unzip -l "$RAW/omni.ja" | tail -1)"
