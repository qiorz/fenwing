#!/bin/bash
# gen-webrender2.sh — 按 RunCbindgen.py 的方式用 cbindgen 0.27 + 已有 metadata 生成头文件
set -u
cd /home/dev/ff/gecko
export PATH="$HOME/.cargo/bin:/opt/ohos-sdk/native/llvm/bin:/usr/local/bin:/usr/bin:/bin"
OUT=gfx/webrender_bindings/webrender_ffi_generated.h
META=obj-aarch64-unknown-linux-ohos/config/cbindgen-metadata.json
ls -l "$META"
cbindgen --version
cbindgen /home/dev/ff/gecko --lockfile Cargo.lock --crate webrender_bindings \
  --metadata "$META" --cpp-compat > "$OUT" 2>/tmp/cbindgen.err
rc=$?
echo "gen_rc=$rc bytes=$(wc -c < "$OUT")"
tail -5 /tmp/cbindgen.err
head -6 "$OUT"
echo "=== [COUNT] occurrences ==="
grep -c '\[COUNT\]' "$OUT" || true
grep -n 'BudgetType_VALUES\|BudgetType_COUNT' "$OUT" | head -4
