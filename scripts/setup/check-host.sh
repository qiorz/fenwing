#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== is there a --host option? ==="
grep -rn '"--host"' build/moz.configure/*.configure | head -5
echo
echo "=== host alias / split_triplet pieces ==="
grep -n "host_alias\|split_triplet" build/moz.configure/init.configure | head -20
echo
echo "=== rust linux targets (ours) ==="
rustc --print target-list 2>/dev/null | grep -E '^x86_64-unknown-linux' | head
echo
echo "=== configure --help | grep host (if supported) ==="
./mach --no-interactive configure --help 2>/dev/null | grep -i -- "--host" | head -5
