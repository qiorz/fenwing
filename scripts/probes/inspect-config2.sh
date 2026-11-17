#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== [1] clang version checks in toolchain.configure ==="
grep -n "clang" build/moz.configure/toolchain.configure | grep -i "version\|minimum\|17\|16\|15" | head -20
echo
echo "=== [2] toolchain.configure diff (ohos) ==="
git diff build/moz.configure/toolchain.configure | head -80
echo
echo "=== [3] mozconfig-ish files added by patch ==="
git status --porcelain | grep -i "mozconfig\|\.mozconfig" | head -20
echo
echo "=== [4] docs referencing configure options ==="
grep -rn "ac_add_options\|--enable-application\|--disable-jemalloc\|--with-clang-path" /mnt/d/ff-ohos/port/ohos_gecko/docs/ /mnt/d/ff-ohos/port/ohos_gecko/README.md 2>/dev/null | head -20
echo
echo "=== [5] mobile/ohos/moz.build ==="
sed -n '1,140p' mobile/ohos/moz.build
echo
echo "=== [6] widget toolkit wiring ==="
grep -rn "MOZ_WIDGET_TOOLKIT" mobile/ohos/ toolkit/moz.configure build/moz.configure/init.configure 2>/dev/null | head -15
echo
echo "=== [7] init.configure diff ohos hunks ==="
git diff build/moz.configure/init.configure | grep -n -A6 -B4 -i "ohos" | head -60
echo
echo "=== [8] flags/finalize-flags diff ohos ==="
git diff build/moz.configure/flags.configure build/moz.configure/finalize-flags.configure | grep -n -A10 -B4 -i "ohos" | head -80
