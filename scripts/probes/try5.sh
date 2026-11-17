#!/bin/bash
# try5.sh — 装 nodejs 后重跑 configure
set -u
cd /home/dev/ff/gecko
export PATH="$HOME/.cargo/bin:/opt/ohos-sdk/native/llvm/bin:/usr/local/bin:$PATH"
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"
export RUSTUP_TOOLCHAIN=stable

echo "=== node state ==="
which node nodejs npm 2>/dev/null || echo "node MISSING"
if ! command -v node >/dev/null 2>&1; then
  echo "installing nodejs/npm via apt ..."
  sudo apt-get install -y --no-install-recommends nodejs npm 2>&1 | tail -3
fi
node --version 2>/dev/null || nodejs --version 2>/dev/null || echo "still missing"

echo "=== configure ==="
./mach --no-interactive configure > /home/dev/ff/configure5.log 2>&1
rc=$?
echo "CONFIGURE_RC=$rc"
tail -22 /home/dev/ff/configure5.log
echo "=== error lines ==="
grep -a -n "ERROR\|Exception\|error:" /home/dev/ff/configure5.log | tail -10
echo TRY5_DONE
