#!/bin/bash
# run-configure.sh — 首次 mach configure（dev 用户）
set -u
cd /home/dev/ff/gecko
cp /mnt/d/ff-ohos/scripts/mozconfig ./mozconfig
chmod +x ./mach

export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export PATH="/opt/ohos-sdk/native/llvm/bin:$HOME/.cargo/bin:/usr/local/bin:$PATH"
export RUSTUP_TOOLCHAIN=stable
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"

echo "=== env ==="
echo "OHOS_SDK_NATIVE=$OHOS_SDK_NATIVE"
which clang; clang --version | head -2
which rustc; rustc --version
python3 --version

echo "=== mach configure (first run) ==="
./mach --no-interactive configure 2>&1 | tee /home/dev/ff/configure.log
rc=${PIPESTATUS[0]}
echo "CONFIGURE_RC=$rc"
echo "=== tail ==="
tail -60 /home/dev/ff/configure.log
echo "RUN_CONFIGURE_DONE"
