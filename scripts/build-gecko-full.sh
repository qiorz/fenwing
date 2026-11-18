#!/bin/bash
# build-gecko-full.sh — 全量构建 libxul/libgeckoview（后台，日志 /home/dev/ff/gecko-build.log）
set -u
cd /home/dev/ff/gecko
export PATH="/opt/ohos-sdk/native/llvm/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"
export RUSTUP_TOOLCHAIN=stable
cp -f /mnt/d/ff-ohos/logs/mozconfig-working.txt ./mozconfig
echo "=== full build start $(date) ==="
nice -n 10 ./mach build -j 8 > /home/dev/ff/gecko-build.log 2>&1
rc=$?
echo "=== full build end $(date) rc=$rc ==="
echo "--- tail (bytes) ---"
tail -c 5000 /home/dev/ff/gecko-build.log
echo
echo "--- first error lines ---"
grep -a -m 5 -n 'error:' /home/dev/ff/gecko-build.log || true
echo GECKO_FULL_DONE rc=$rc
