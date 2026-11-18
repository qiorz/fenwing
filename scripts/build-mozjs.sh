#!/bin/bash
# build-mozjs.sh — 用已打补丁的 Gecko 142 树构建 SpiderMonkey（js 项目，M1/G1）
set -u
cd /home/dev/ff/gecko
export PATH="/opt/ohos-sdk/native/llvm/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"
export RUSTUP_TOOLCHAIN=stable
export MOZ_OBJDIR=/home/dev/ff/obj-js
mkdir -p "$MOZ_OBJDIR"

cat > ./mozconfig <<'EOF'
ac_add_options --enable-project=js
ac_add_options --target=aarch64-unknown-linux-ohos
ac_add_options --host=x86_64-unknown-linux-gnu
ac_add_options --enable-shared-js
ac_add_options --disable-bootstrap
ac_add_options --enable-optimize
ac_add_options --disable-debug
ac_add_options --disable-tests
ac_add_options --disable-jemalloc
ac_add_options --disable-jit
ac_add_options --disable-dtrace
ac_add_options --disable-profiling
ac_add_options --without-intl-api
EOF

echo "=== configure (js) $(date) ==="
./mach --no-interactive configure > /home/dev/ff/js-configure.log 2>&1
rc=$?
echo "JS_CONFIGURE_RC=$rc"
if [ $rc -ne 0 ]; then
  tail -25 /home/dev/ff/js-configure.log
  echo JS_CONFIGURE_FAILED
  exit 1
fi

echo "=== build (js) $(date) ==="
nice -n 10 ./mach build -j 8 > /home/dev/ff/js-build.log 2>&1
rc=$?
echo "JS_BUILD_RC=$rc  $(date)"
tail -20 /home/dev/ff/js-build.log

mkdir -p /mnt/d/ff-ohos/artifacts/mozjs
cp -v "$MOZ_OBJDIR"/dist/bin/libmozjs*.so /mnt/d/ff-ohos/artifacts/mozjs/ 2>/dev/null
cp "$MOZ_OBJDIR"/dist/include/jsapi.h "$MOZ_OBJDIR"/dist/include/js/*.h /mnt/d/ff-ohos/artifacts/mozjs/ 2>/dev/null
find "$MOZ_OBJDIR/dist" -maxdepth 3 \( -name 'libmozjs*' -o -name 'jsapi.h' \) -printf '%p\n' 2>/dev/null | head -20
ls -lh /mnt/d/ff-ohos/artifacts/mozjs/ 2>/dev/null | head
echo JS_JOB_DONE rc=$rc
