#!/bin/bash
# extract-sdk.sh — 解出 OpenHarmony 7.0 (API 26) Linux native SDK
set -e
SRC=/mnt/d/ff-ohos/setup/ohos-sdk-windows_linux-public.tar.gz
ZIPNAME=native-linux-x64-26.0.0.38-Beta.zip
mkdir -p /opt/ohos-sdk
cd /opt/ohos-sdk
echo "=== tar extract ($ZIPNAME) ==="
tar -xzf "$SRC" "ohos-sdk/linux/$ZIPNAME"
ls -lh "ohos-sdk/linux/$ZIPNAME"
echo "=== unzip -> /opt/ohos-sdk/native ==="
unzip -o -q "ohos-sdk/linux/$ZIPNAME" -d native
echo "=== native tree ==="
ls -la native
echo "=== version ==="
cat native/oh-uni-package.json
echo "=== clang ==="
native/llvm/bin/clang --version
echo "=== sysroot ==="
ls native/sysroot/usr/lib/ | head
echo "=== hdc? ==="
find /opt/ohos-sdk -name 'hdc' -type f 2>/dev/null | head
echo "EXTRACT_SDK_DONE"
