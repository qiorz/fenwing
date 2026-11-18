#!/bin/bash
# fix-cbindgen.sh — Gecko 142 生成头需要 cbindgen 0.27.x（0.29 生成了不兼容的 COUNT）
set -eu
export PATH="$HOME/.cargo/bin:/opt/ohos-sdk/native/llvm/bin:/usr/local/bin:/usr/bin:/bin"
echo "before: $(cbindgen --version)"
cargo install cbindgen --version 0.27.0 --force --locked 2>&1 | tail -3
echo "after: $(cbindgen --version)"
rm -f /home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/include/mozilla/webrender/webrender_ffi_generated.h
echo "removed stale generated header"
