#!/bin/bash
set -u
cd /home/dev/ff/gecko
D=obj-aarch64-unknown-linux-ohos/dist/include/mozilla/webrender/webrender_ffi_generated.h
echo "=== dist path stat ==="; ls -l "$D" 2>&1; head -5 "$D" 2>/dev/null
echo "=== tracked in git? ==="
git ls-files gfx/webrender_bindings/webrender_ffi_generated.h
git status --porcelain gfx/webrender_bindings/webrender_ffi_generated.h
echo "=== restore from git if tracked ==="
git checkout -- gfx/webrender_bindings/webrender_ffi_generated.h 2>&1 && echo RESTORED || echo NO_RESTORE
ls -l gfx/webrender_bindings/webrender_ffi_generated.h 2>&1
grep -n 'BudgetType_VALUES' gfx/webrender_bindings/webrender_ffi_generated.h 2>/dev/null | head -2
echo "=== remove stale dist copy ==="
rm -f "$D"
ls -l "$D" 2>&1
