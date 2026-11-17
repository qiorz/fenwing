#!/bin/bash
set -u
for f in /mnt/d/ff-ohos/artifacts/gecko/libxul-stripped.so /mnt/d/ff-ohos/work/firefoxport/gecko/libs/arm64-v8a/libxul.so; do
  echo "== $f"
  /opt/ohos-sdk/native/llvm/bin/llvm-readelf -S "$f" 2>/dev/null | grep -i permission || echo '  no .permission section'
done
