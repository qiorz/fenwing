#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== message source ==="
grep -rn "Don't know how to translate" build/ python/ 2>/dev/null | head -5
echo
echo "=== rust.configure: host/target triplet mapping ==="
grep -n "host\|target" build/moz.configure/rust.configure | head -60
echo
echo "=== relevant block ==="
awk 'NR>=1 && /def rust_toolchain|rust_target|host_triplet|split_triplet|spew|die\(/ {print NR": "$0}' build/moz.configure/rust.configure | head -40
echo
echo "=== target triple mapping table ==="
sed -n '1,140p' build/moz.configure/rust.configure
