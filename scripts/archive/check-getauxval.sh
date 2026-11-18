#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== xsimd getauxval 用法 ==="
grep -rn "getauxval" third_party/xsimd/include/xsimd/config/xsimd_cpuid.hpp | head -10
echo
echo "=== 上下文 ==="
grep -n -B12 -A20 "getauxval" third_party/xsimd/include/xsimd/config/xsimd_cpuid.hpp | head -80
echo
echo "=== sysroot libc getauxval? ==="
nm -D /opt/ohos-sdk/native/sysroot/usr/lib/aarch64-linux-ohos/libc.so 2>/dev/null | grep -i getauxval || echo "NOT EXPORTED"
echo
echo "=== js/moz.configure wasm 选项 ==="
grep -rn "disable-wasm\|enable-wasm" js/src/moz.configure js/src/configure.py 2>/dev/null | head -10
