#!/bin/bash
set -u
S=/home/dev/ff/gecko/gfx/webrender_bindings/webrender_ffi_generated.h
echo "=== source header stat ==="; ls -l "$S" 2>&1
echo "=== header first 12 lines ==="; head -12 "$S" 2>/dev/null
echo "=== generated how? ==="
grep -rn "webrender_ffi_generated" /home/dev/ff/gecko/gfx/webrender_bindings/moz.build /home/dev/ff/gecko/gfx/webrender_bindings/*.toml /home/dev/ff/gecko/gfx/webrender_bindings/build.rs 2>/dev/null | head -10
echo "=== cbindgen in Cargo.toml/lock ==="
grep -rn "cbindgen" /home/dev/ff/gecko/gfx/webrender_bindings/Cargo.toml /home/dev/ff/gecko/Cargo.lock 2>/dev/null | head -8
echo "=== build log cbindgen/generate lines ==="
grep -a -n -i 'cbindgen\|webrender_ffi_generated' /home/dev/ff/gecko-build.log | head -10
echo "=== which cbindgen on build PATH ==="
PATH="/opt/ohos-sdk/native/llvm/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin" bash -lc 'which cbindgen; cbindgen --version'
