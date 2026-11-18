#!/bin/bash
set -eu
W=/mnt/d/ff-ohos/work/firefoxport
L=$W/gecko/libs/arm64-v8a
B=/mnt/d/ff-ohos/artifacts/libs-backup-p23
mkdir -p "$B"
echo "=== backup ==="
if [ ! -f "$B/libxul.so" ]; then
  cp -f "$L"/*.so "$B"/ 2>/dev/null || true
fi
echo "=== strip .so (keep backups) ==="
STRIP=/opt/ohos-sdk/native/llvm/bin/llvm-strip
if [ ! -x "$STRIP" ]; then STRIP=$(command -v llvm-strip || true); fi
echo "strip=$STRIP"
before=$(du -sb "$L" | cut -f1)
for f in "$L"/*.so; do
  "$STRIP" --strip-unneeded "$f" 2>/dev/null || true
done
after=$(du -sb "$L" | cut -f1)
echo "libs bytes before=$before after=$after"
du -sh "$L"
ls -lS "$L" | head -6
