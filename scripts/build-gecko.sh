#!/bin/bash
# build-gecko.sh — 全量构建 libxul/libgeckoview（后台跑，日志在 /home/dev/ff/build.log）
# 用法：bash build-gecko.sh [并行数，默认 8]
set -u
JOBS="${1:-8}"
cd /home/dev/ff/gecko
export PATH="/opt/ohos-sdk/native/llvm/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"
export RUSTUP_TOOLCHAIN=stable
export MOZ_CONFIGURE_ARGS=""
cp /mnt/d/ff-ohos/logs/mozconfig-working.txt ./mozconfig

echo "=== build start $(date) jobs=$JOBS ==="
nice -n 10 ./mach build -j"$JOBS" > /home/dev/ff/build.log 2>&1
rc=$?
echo "=== build end $(date) rc=$rc ==="
tail -30 /home/dev/ff/build.log
ls -lh obj-aarch64-unknown-linux-ohos/dist/bin/ 2>/dev/null | head -40
echo BUILD_DONE rc=$rc
