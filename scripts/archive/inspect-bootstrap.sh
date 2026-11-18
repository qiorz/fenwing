#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== bootstrap.configure 1-60 ==="
sed -n '1,60p' build/moz.configure/bootstrap.configure
echo
echo "=== bootstrap.configure 240-300 ==="
sed -n '240,300p' build/moz.configure/bootstrap.configure
echo
echo "=== configure.log: artifact / error context ==="
grep -n -B5 -A20 "artifact.*toolchain\|toolchain-linux64-clang" /home/dev/ff/configure.log | head -80
echo
echo "=== network probes from WSL ==="
for h in firefox-ci-tc.services.mozilla.com archive.mozilla.org hg.mozilla.org; do
  if curl -sS -o /dev/null -w "%{http_code}" --max-time 8 "https://$h/" 2>/dev/null; then echo " <- $h"; else echo "FAIL $h"; fi
done
