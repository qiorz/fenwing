#!/bin/bash
set -u
cd /home/dev/ff/gecko
grep -rn 'AIRWEB_FORCE_NO_JIT' --include=*.cpp --include=*.h . | head -10
echo "=== XPCOMInit JIT detection ==="
F=$(grep -rl 'AIRWEB_FORCE_NO_JIT' --include=*.cpp . | head -1)
echo "file: $F"
grep -n 'AIRWEB_FORCE_NO_JIT' -B 40 -A 60 "$F" | head -160
