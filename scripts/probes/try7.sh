#!/bin/bash
# try7.sh — NDK clang 作主编译器 + 系统 clang 作 wasm 编译器
set -u
cd /home/dev/ff/gecko
export PATH="/opt/ohos-sdk/native/llvm/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"
export RUSTUP_TOOLCHAIN=stable
export WASM_CC=/usr/bin/clang
export WASM_CXX=/usr/bin/clang++
export WASM_LD=/usr/bin/wasm-ld

echo "clang -> $(which clang)"
clang --version | head -1
echo "wasm cc -> $WASM_CC"

./mach --no-interactive configure > /home/dev/ff/configure7.log 2>&1
rc=$?
echo "CONFIGURE_RC=$rc"
tail -18 /home/dev/ff/configure7.log
echo "=== error lines ==="
grep -a -n "ERROR\|Exception\|error:" /home/dev/ff/configure7.log | tail -8
echo TRY7_DONE
