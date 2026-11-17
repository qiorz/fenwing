#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== clang version requirement ==="
grep -n "clang version\|clang_version\|minimum.*clang\|Clang 1" build/moz.configure/toolchain.configure | head -20
echo
echo "=== toolchain.configure ohos-related hunks ==="
grep -n -i "ohos" build/moz.configure/toolchain.configure | head -20
echo
echo "=== init.configure ohos ==="
grep -n -i "ohos" build/moz.configure/init.configure | head -20
echo
echo "=== flags.configure ohos ==="
grep -n -i "ohos" build/moz.configure/flags.configure build/moz.configure/finalize-flags.configure | head -20
echo
echo "=== mobile/ohos/moz.configure (120-end) ==="
sed -n '120,260p' mobile/ohos/moz.configure
echo
echo "=== mobile/ohos/moz.build ==="
sed -n '1,120p' mobile/ohos/moz.build
echo
echo "=== project flags / widget toolkit ==="
grep -rn "MOZ_WIDGET_TOOLKIT" mobile/ohos/ | head -10
