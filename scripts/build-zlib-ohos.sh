#!/bin/bash
# build-zlib-ohos.sh — 为 OHOS aarch64 构建 zlib 共享库（设备上没有 libz.so）
set -eu
NDK=/opt/ohos-sdk/native
SYSROOT=$NDK/sysroot
CC=$NDK/llvm/bin/clang
W=/mnt/d/ff-ohos/work/firefoxport
LIBS=$W/gecko/src/main/libs/arm64-v8a
LIBS2=$W/gecko/libs/arm64-v8a
TMP=/home/dev/ff/third_party_build
mkdir -p "$TMP" "$LIBS" "$LIBS2"
cd "$TMP"

if [ ! -d zlib-1.3.1 ]; then
  if [ ! -f zlib-1.3.1.tar.gz ]; then
    curl -sSL --retry 3 -o zlib-1.3.1.tar.gz https://github.com/madler/zlib/archive/refs/tags/v1.3.1.tar.gz
  fi
  tar xzf zlib-1.3.1.tar.gz
fi
cd zlib-1.3.1

echo "=== build libz.so ==="
$CC --target=aarch64-linux-ohos --sysroot="$SYSROOT" -O2 -fPIC -shared \
  -Wl,-soname,libz.so -Wl,--build-id -o libz.so \
  adler32.c compress.c crc32.c deflate.c gzclose.c gzlib.c gzread.c gzwrite.c \
  infback.c inffast.c inflate.c inftrees.c trees.c uncompr.c zutil.c
ls -lh libz.so
/opt/ohos-sdk/native/llvm/bin/llvm-readelf -d libz.so | grep -E 'SONAME|NEEDED'

cp -f libz.so "$LIBS/libz.so"
cp -f libz.so "$LIBS2/libz.so"
echo "staged -> $LIBS/libz.so"
echo ZLIB_DONE
