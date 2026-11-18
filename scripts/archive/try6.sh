#!/bin/bash
# try6.sh — 用系统 clang 当 wasm 编译器，重跑 configure
set -u
cd /home/dev/ff/gecko
export PATH="$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin:/opt/ohos-sdk/native/llvm/bin"
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"
export RUSTUP_TOOLCHAIN=stable
export WASM_CC=/usr/bin/clang
export WASM_CXX=/usr/bin/clang++
export WASM_LD=/usr/bin/wasm-ld

echo "=== check wasm tools ==="
/usr/bin/wasm-ld --version 2>/dev/null | head -1 || echo "no wasm-ld"
echo "=== sandbox-related options ==="
grep -rn "sandboxed-libraries\|wasm_sandbox\|WASM_SANDBOX" build/moz.configure/ | head -10

echo "=== configure ==="
./mach --no-interactive configure > /home/dev/ff/configure6.log 2>&1
rc=$?
echo "CONFIGURE_RC=$rc"
tail -20 /home/dev/ff/configure6.log
echo "=== error lines ==="
grep -a -n "ERROR\|Exception\|error:" /home/dev/ff/configure6.log | tail -8
echo TRY6_DONE
