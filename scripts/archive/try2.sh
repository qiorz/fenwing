#!/bin/bash
# try2.sh — 诊断 artifact 失败 + 用 --disable-bootstrap 重跑 configure（输出只留尾部）
set -u
cd /home/dev/ff/gecko
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export PATH="/opt/ohos-sdk/native/llvm/bin:$HOME/.cargo/bin:/usr/local/bin:$PATH"
export RUSTUP_TOOLCHAIN=stable
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"

echo "=== artifact toolchain (manual, tail 25) ==="
./mach --log-no-times artifact toolchain --from-build toolchain-linux64-clang 2>&1 | tail -25
echo "ARTIFACT_RC=${PIPESTATUS[0]}"

echo
echo "=== mozconfig: use --disable-bootstrap ==="
cat > ./mozconfig <<'EOF'
ac_add_options --enable-application=mobile/ohos
ac_add_options --target=aarch64-unknown-linux-ohos
ac_add_options --disable-bootstrap
ac_add_options --disable-jemalloc
ac_add_options --enable-optimize
ac_add_options --disable-debug
ac_add_options --disable-tests
ac_add_options --disable-updater
ac_add_options --disable-crashreporter
EOF
cat ./mozconfig

echo
echo "=== configure (tail 30) ==="
./mach --no-interactive configure > /home/dev/ff/configure2.log 2>&1
rc=$?
echo "CONFIGURE_RC=$rc"
tail -30 /home/dev/ff/configure2.log
echo "=== error lines ==="
grep -a -n "ERROR\|Exception\|error:" /home/dev/ff/configure2.log | tail -15
echo "RUN2_DONE"
