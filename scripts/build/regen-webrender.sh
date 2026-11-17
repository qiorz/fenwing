#!/bin/bash
# regen-webrender.sh — 用 cbindgen 0.27 手工生成 webrender_ffi_generated.h
set -u
cd /home/dev/ff/gecko
export PATH="$HOME/.cargo/bin:/opt/ohos-sdk/native/llvm/bin:/usr/local/bin:/usr/bin:/bin"
cbindgen --version
cbindgen toolkit/library/rust/ --lockfile Cargo.lock --crate webrender_bindings \
  -o gfx/webrender_bindings/webrender_ffi_generated.h 2>&1 | tail -10
echo "rc=$?"
ls -l gfx/webrender_bindings/webrender_ffi_generated.h 2>/dev/null
head -6 gfx/webrender_bindings/webrender_ffi_generated.h 2>/dev/null
echo "=== COUNT usage ==="
grep -n 'BudgetType_VALUES\|BudgetType_COUNT' gfx/webrender_bindings/webrender_ffi_generated.h | head -4
echo "=== any bare [COUNT] lines ==="
grep -cn '\[COUNT\]' gfx/webrender_bindings/webrender_ffi_generated.h
