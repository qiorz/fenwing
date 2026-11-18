#!/bin/bash
# fix-sdk.sh — 把 SDK 目录结构拍平并自检（root 运行）
set -u
cd /opt/ohos-sdk
echo "=== before ==="
ls -la .
ls -la native
if [ -d native/native ]; then
  echo "=== flattening native/native -> native ==="
  for x in native/native/*; do
    mv "$x" native/
  done
  rmdir native/native 2>/dev/null || true
fi
echo "=== after ==="
ls -la native
echo "=== version json ==="
cat native/oh-uni-package.json 2>/dev/null || echo "no oh-uni-package.json"
echo "=== clang ==="
native/llvm/bin/clang --version 2>&1 | head -3
echo "=== sysroot arch dirs ==="
ls native/sysroot/usr/lib/ 2>/dev/null | head
echo "=== libc++ ==="
find native -name 'libc++*' -maxdepth 6 2>/dev/null | head -10
echo "=== cmake/ninja ==="
ls native/build-tools/cmake/bin 2>/dev/null | head
echo "FIX_SDK_DONE"
