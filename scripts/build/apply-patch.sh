#!/bin/bash
# apply-patch.sh — 去掉 CRLF 后应用全量补丁（dev 运行）
set -u
cd /home/dev/ff/gecko
cp /mnt/d/ff-ohos/port/ohos_gecko/patches/full/ohos-v271-vs-upstream-5836a062726f.patch /tmp/ohos-full.patch
sed -i 's/\r$//' /tmp/ohos-full.patch
echo "CR-lines left: $(grep -c $'\r' /tmp/ohos-full.patch || true)"
git apply --check -p1 /tmp/ohos-full.patch && echo CHECK_OK || { echo CHECK_FAILED; exit 1; }
git apply -p1 /tmp/ohos-full.patch && echo APPLY_OK || { echo APPLY_FAILED; exit 1; }
echo "changed files: $(git status --porcelain | wc -l)"
echo "=== key build files ==="
ls -la build/moz.configure/ohos-ndk.configure build/moz.configure/ohos-sdk.configure mobile/ohos/moz.configure mobile/ohos/confvars.sh build/moz.configure/init.configure 2>&1
echo "=== ohos-ndk.configure ==="
cat build/moz.configure/ohos-ndk.configure
echo "=== mobile/ohos/confvars.sh ==="
cat mobile/ohos/confvars.sh
echo "=== mobile/ohos/moz.configure ==="
sed -n '1,120p' mobile/ohos/moz.configure
