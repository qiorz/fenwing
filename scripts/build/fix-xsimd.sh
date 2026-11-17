#!/bin/bash
# fix-xsimd.sh — OHOS 下跳过 getauxval（sysroot 动态符号在 hidden 引用下不可用），然后增量重编 JS
set -u
cd /home/dev/ff/gecko
H=third_party/xsimd/include/xsimd/config/xsimd_cpuid.hpp
mkdir -p /mnt/d/ff-ohos/scripts/patches

echo "=== patch xsimd guards ==="
sed -i 's|#if defined(__linux__) \&\& (!defined(__ANDROID_API__) || __ANDROID_API__ >= 18)|#if defined(__linux__) \&\& !defined(__OHOS__) \&\& (!defined(__ANDROID_API__) || __ANDROID_API__ >= 18)|g' "$H"
grep -n "defined(__linux__)" "$H" | head
git diff -- "$H" > /mnt/d/ff-ohos/scripts/patches/0002-xsimd-skip-getauxval-on-ohos.patch
wc -l /mnt/d/ff-ohos/scripts/patches/0002-xsimd-skip-getauxval-on-ohos.patch

echo "=== rebuild js (incremental) ==="
export PATH="/opt/ohos-sdk/native/llvm/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"
export RUSTUP_TOOLCHAIN=stable
export MOZ_OBJDIR=/home/dev/ff/obj-js
nice -n 10 ./mach build -j 8 > /home/dev/ff/js-build2.log 2>&1
rc=$?
echo "JS_BUILD2_RC=$rc"
tail -15 /home/dev/ff/js-build2.log
ls -lh /home/dev/ff/obj-js/dist/bin/libmozjs* 2>/dev/null
cp -v /home/dev/ff/obj-js/dist/bin/libmozjs*.so /mnt/d/ff-ohos/artifacts/mozjs/ 2>/dev/null
cp /home/dev/ff/obj-js/dist/include/jsapi.h /mnt/d/ff-ohos/artifacts/mozjs/ 2>/dev/null
mkdir -p /mnt/d/ff-ohos/artifacts/mozjs/include
cp /home/dev/ff/obj-js/dist/include/js/*.h /mnt/d/ff-ohos/artifacts/mozjs/include/ 2>/dev/null
ls -lh /mnt/d/ff-ohos/artifacts/mozjs/ | head
echo JS_FIX_DONE rc=$rc
