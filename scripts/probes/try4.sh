#!/bin/bash
# try4.sh — 装 cbindgen 后重跑 configure
set -u
cd /home/dev/ff/gecko
export PATH="$HOME/.cargo/bin:/opt/ohos-sdk/native/llvm/bin:/usr/local/bin:$PATH"
export RUSTUP_TOOLCHAIN=stable

echo "=== required cbindgen version ==="
grep -rn "cbindgen" build/moz.configure/rust.configure | grep -i "version\|0\." | head -10

echo "=== cargo install cbindgen ==="
VER=$(grep -oE 'cbindgen_version = Version\("[0-9.]+"\)|cbindgen_min_version = "[0-9.]+"' build/moz.configure/rust.configure | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || true)
echo "VER=$VER"
CARGO_BUILD_JOBS=12 cargo install cbindgen ${VER:+--version $VER} --locked 2>&1 | tail -5
echo "CBINDGEN_RC=$?"
which cbindgen && cbindgen --version

echo "=== configure ==="
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"
./mach --no-interactive configure > /home/dev/ff/configure4.log 2>&1
rc=$?
echo "CONFIGURE_RC=$rc"
tail -20 /home/dev/ff/configure4.log
echo "=== error lines ==="
grep -a -n "ERROR\|Exception\|error:" /home/dev/ff/configure4.log | tail -10
echo TRY4_DONE
