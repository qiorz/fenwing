#!/bin/bash
set -u
cd /home/dev/ff/gecko
H=obj-aarch64-unknown-linux-ohos/dist/include/mozilla/webrender/webrender_ffi_generated.h
S=gfx/webrender_bindings/webrender_ffi_generated.h
echo "=== dist path ==="; ls -l "$H" 2>&1
echo "=== source path ==="; ls -l "$S" 2>&1; head -6 "$S" 2>/dev/null
echo "=== bare [COUNT] count ==="; grep -c '\[COUNT\]' "$S" 2>/dev/null || true
echo "=== CbindgenHeader impl ==="
grep -rn 'CbindgenHeader' /home/dev/ff/gecko/python /home/dev/ff/gecko/build 2>/dev/null | head -6
