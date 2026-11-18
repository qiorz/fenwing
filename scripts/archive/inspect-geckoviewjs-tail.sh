#!/bin/bash
set -u
F=/home/dev/ff/gecko/mobile/shared/chrome/geckoview/geckoview.js
echo "=== contentTitle / DOMTitleChanged usages ==="
grep -n 'contentTitle\|DOMTitleChanged\|contentDocument' "$F" | head -10
echo
echo "=== tail of file (last 40 lines) ==="
tail -40 "$F"
echo
echo "=== startup function ==="
grep -n 'function startup\|startup(' "$F" | head -5
