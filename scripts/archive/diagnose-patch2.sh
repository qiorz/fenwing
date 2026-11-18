#!/bin/bash
set -u
cd /home/dev/ff/gecko
P=/tmp/ohos-full.patch
echo "=== blob hashes vs patch index ==="
for f in widget/Theme.cpp toolkit/library/moz.build third_party/libwebrtc/modules/audio_processing/agc2/gain_map_gn/moz.build toolkit/moz.configure; do
  h=$(git hash-object "$f")
  echo "$f -> $h"
done
echo "--- expected a-side from patch ---"
grep -A1 "^diff --git a/widget/Theme.cpp" "$P" | grep '^index'
grep -A1 "^diff --git a/toolkit/library/moz.build" "$P" | grep '^index'
grep -A1 "^diff --git a/toolkit/moz.configure" "$P" | grep '^index'
echo "=== single file check rc ==="
git apply --check --include='widget/Theme.cpp' "$P"; echo "Theme.cpp rc=$?"
git apply --check --include='toolkit/library/moz.build' "$P"; echo "toolkit/library rc=$?"
git apply --check --include='toolkit/moz.configure' "$P"; echo "toolkit/moz.configure rc=$?"
echo "=== sample failing gn file ==="
f='third_party/libwebrtc/modules/audio_processing/agc2/gain_map_gn/moz.build'
git apply --check --include="$f" "$P"; echo "gn rc=$?"
echo "=== diff of that file: first 15 lines ==="
sed -n '1,15p' "$f"
echo "=== patch hunk for it ==="
grep -A14 "^diff --git a/$f" "$P" | head -20
