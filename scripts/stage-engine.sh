#!/bin/bash
# stage-engine.sh — 把 libxul / libgeckoview / NSS+NSPR 依赖 / NDK stub 库放进 HSP 的 libs
set -eu
B=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin
NDK=/opt/ohos-sdk/native
W=/mnt/d/ff-ohos/work/firefoxport
LIBS=$W/gecko/libs/arm64-v8a
SRC_LIBS=$W/gecko/src/main/libs/arm64-v8a
mkdir -p "$LIBS"

echo "=== 1) libxul (stripped) ==="
cp -f /mnt/d/ff-ohos/artifacts/gecko/libxul-stripped.so "$LIBS/libxul.so"
cp -f /mnt/d/ff-ohos/artifacts/gecko/libxul-stripped.so "$SRC_LIBS/libxul.so"
echo "libxul: $(du -h "$LIBS/libxul.so" | cut -f1)"

echo "=== 2) libgeckoview + geckoxcomp 副本 ==="
cp -f "$B/libgeckoview.so" "$LIBS/libgeckoview.so"
# geckoxcomp 是同一份 NAPI 模块的副本，供 XComponent 触发注册；必须删 build-id，
# 否则 dlopen 会按 build-id 复用映像、constructor 不触发。
cp -f /mnt/d/ff-ohos/artifacts/gecko/libxul-stripped.so /dev/null 2>/dev/null || true
cp -f "$B/libgeckoview.so" "$LIBS/libgeckoxcomp.so"
$NDK/llvm/bin/llvm-objcopy --remove-section=.note.gnu.build-id "$LIBS/libgeckoxcomp.so" 2>/dev/null || \
  $NDK/llvm/bin/llvm-strip --remove-section=.note.gnu.build-id "$LIBS/libgeckoxcomp.so" 2>/dev/null || true

echo "=== 3) NSS/NSPR/ffvpx 运行时依赖 ==="
for l in libnspr4.so libplc4.so libplds4.so libgkcodecs.so liblgpllibs.so libnss3.so \
         libnssutil3.so libsmime3.so libmozsqlite3.so libssl3.so libsoftokn3.so \
         libfreebl3.so libmozavcodec.so libmozavutil.so; do
  if [ -f "$B/$l" ]; then cp -f "$B/$l" "$LIBS/$l"; else echo "MISS $l"; fi
done

echo "=== 4) NDK 系统 stub 库 ==="
for l in libohinputmethod.so libtime_service_ndk.so; do
  src=$NDK/sysroot/usr/lib/aarch64-linux-ohos/$l
  if [ -f "$src" ]; then cp -f "$src" "$LIBS/$l"; else echo "MISS $l"; fi
done

echo "=== 5) 清点 ==="
ls -lh "$LIBS" | head -40
echo "total: $(du -sh "$LIBS" | cut -f1)"
