#!/bin/bash
set -u
G=/home/dev/ff/gecko
B=$G/obj-aarch64-unknown-linux-ohos/dist/bin
A=/mnt/d/ff-ohos/artifacts/gecko
NDK=/opt/ohos-sdk/native
STRIP=$NDK/llvm/bin/llvm-strip
READELF=$NDK/llvm/bin/llvm-readelf

echo "=== ports/ohos/permission.json ==="
cat "$G/ports/ohos/permission.json" 2>/dev/null || echo "missing"
echo
echo "=== strip libxul (copy) ==="
cp -f "$B/libxul.so" "$A/libxul-stripped.so"
$STRIP --strip-unneeded "$A/libxul-stripped.so"
ls -lh "$B/libxul.so" "$A/libxul-stripped.so"
echo
echo "=== NDK system libs needed ==="
for l in libc++_shared.so libohinputmethod.so libtime_service_ndk.so libohaudio.so libnative_window.so libnative_display_manager.so; do
  p=$(find "$NDK/sysroot/usr/lib/aarch64-linux-ohos" -maxdepth 1 -name "$l" 2>/dev/null | head -1)
  if [ -n "$p" ]; then echo "FOUND $l -> $(basename "$p") $(stat -c%s "$p") bytes"; else echo "MISS  $l"; fi
done
echo
echo "=== post_build script in port repo? ==="
ls -l "$G/../ohos_gecko" 2>/dev/null | head -3
find /mnt/d/ff-ohos/port/ohos_gecko -name 'post_build*' -o -name '*permission*' 2>/dev/null | head -10
