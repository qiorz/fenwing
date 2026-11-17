#!/bin/bash
set -u
cd /home/dev/ff/gecko
P=/tmp/ohos-full.patch
echo "=== patch file type ==="
file "$P"
echo "CRLF count: $(grep -c $'\r' "$P" || true)"
echo "=== raw bytes around Theme.cpp hunk ==="
sed -n '117538,117546p' "$P" | od -c | head -20
echo "=== same lines from actual file (114-120) ==="
sed -n '114,120p' widget/Theme.cpp | od -c | head -20
echo "=== patch dry-run with GNU patch (fuzz allowed) ==="
patch -p1 --dry-run --no-backup-if-mismatch < "$P" 2>&1 | grep -E 'FAILED|fuzz|Hunk|saving|reject' | head -20
echo "=== patch dry-run summary counters ==="
patch -p1 --dry-run --no-backup-if-mismatch < "$P" >/tmp/patchdry.log 2>&1; echo "rc=$?"
grep -c 'FAILED' /tmp/patchdry.log || true
grep -c 'with fuzz' /tmp/patchdry.log || true
grep -c 'Hunk' /tmp/patchdry.log || true
tail -5 /tmp/patchdry.log
