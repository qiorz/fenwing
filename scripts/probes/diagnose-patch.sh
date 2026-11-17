#!/bin/bash
# diagnose-patch.sh
set -u
cd /home/dev/ff/gecko
P=/tmp/ohos-full.patch
echo "=== HEAD ==="
git rev-parse HEAD
git log -1 --format='%an %ad'
echo "=== file type ==="
file widget/Theme.cpp
echo "=== git attributes / autocrlf ==="
git config --get core.autocrlf || echo "(unset)"
echo "=== patch source of widget/Theme.cpp hunk ==="
grep -n -B3 -A12 '^diff --git a/widget/Theme.cpp' "$P" | head -40
echo "=== actual file lines 105-125 ==="
sed -n '105,125p' widget/Theme.cpp
echo "=== single-file apply check (verbose) ==="
git apply --check --verbose --include='widget/Theme.cpp' "$P" 2>&1 | head -20
echo "=== try one more: toolkit/library/moz.build ==="
grep -n -A6 '^diff --git a/toolkit/library/moz.build' "$P" | head -20
sed -n '275,292p' toolkit/library/moz.build
git apply --check --verbose --include='toolkit/library/moz.build' "$P" 2>&1 | head -20
echo "=== count files in patch ==="
grep -c '^diff --git ' "$P"
echo "=== first 40 patch lines ==="
head -40 "$P"
