#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== grep MOZBUILD_CLANG / toolchain-linux64-clang / enable-bootstrap ==="
grep -rn "MOZBUILD_CLANG" --include=*.py --include=*.configure --include=*.toml . 2>/dev/null | head -20
grep -rn "toolchain-linux64-clang" --include=*.py --include=*.configure --include=*.toml . 2>/dev/null | head -10
grep -rn "enable-bootstrap\|no-update" --include=*.configure --include=*.py build/ python/ 2>/dev/null | head -20
echo
echo "=== option definitions related to clang/host compiler ==="
grep -n "option(" build/moz.configure/toolchain.configure | head -60
echo
echo "=== 'with-clang-path' occurrences ==="
grep -rn "with-clang-path\|clang-path" build/moz.configure/*.configure python/mozbuild/mozbuild/*.py 2>/dev/null | head -20
echo
echo "=== bootstrap module names ==="
ls python/mozboot/mozboot/ | head -30
