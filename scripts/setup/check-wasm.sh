#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== wasm-related options ==="
grep -rn "wasm" build/moz.configure/*.configure | grep -i "option\|wasm_cc\|with-wasm\|sandbox" | head -20
echo
echo "=== wasm compiler detection block ==="
grep -rn "wasm C compiler" build/ | head -5
echo
echo "=== system clang wasm test ==="
printf 'int main(void){return 0;}\n' > /tmp/wasmtest.c
/usr/bin/clang --target=wasm32-wasi -c /tmp/wasmtest.c -o /tmp/wasmtest.o && echo "SYSTEM_CLANG_WASM_OK" || echo "SYSTEM_CLANG_WASM_FAIL"
/usr/bin/clang --version | head -1
echo
echo "=== OHOS clang targets ==="
/opt/ohos-sdk/native/llvm/bin/clang --print-targets 2>/dev/null | head -20
echo
echo "=== grep WASM_CC env/option ==="
grep -rn "WASM_CC\|with-wasm\|--enable-wasm" build/moz.configure/ | head -15
