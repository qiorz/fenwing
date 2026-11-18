#!/bin/bash
set -u
H=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/include/mozilla/webrender/webrender_ffi_generated.h
echo "=== header stat ==="; ls -l "$H"
echo "=== COUNT lines ==="; grep -n 'COUNT' "$H" | head -5
echo "=== BudgetType enum ==="; grep -n -B2 -A12 'enum class BudgetType' "$H" | head -30
echo "=== bindings.rs BudgetType ==="; grep -rn -A8 'BudgetType' /home/dev/ff/gecko/gfx/webrender_bindings/src/bindings.rs | head -20
echo "=== build log cbindgen lines ==="; grep -a -n 'cbindgen' /home/dev/ff/gecko-build.log | head -10
echo "=== cbindgen binary used ==="; which cbindgen; cbindgen --version
