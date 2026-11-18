#!/bin/bash
# try3.sh — 加 --host 解决 rust host triplet 映射，再跑 configure
set -u
cd /home/dev/ff/gecko
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export PATH="/opt/ohos-sdk/native/llvm/bin:$HOME/.cargo/bin:/usr/local/bin:$PATH"
export RUSTUP_TOOLCHAIN=stable
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"

cat > ./mozconfig <<'EOF'
ac_add_options --enable-application=mobile/ohos
ac_add_options --target=aarch64-unknown-linux-ohos
ac_add_options --host=x86_64-unknown-linux-gnu
ac_add_options --disable-bootstrap
ac_add_options --disable-jemalloc
ac_add_options --enable-optimize
ac_add_options --disable-debug
ac_add_options --disable-tests
ac_add_options --disable-updater
ac_add_options --disable-crashreporter
EOF

./mach --no-interactive configure > /home/dev/ff/configure3.log 2>&1
rc=$?
echo "CONFIGURE_RC=$rc"
tail -25 /home/dev/ff/configure3.log
echo "=== error lines ==="
grep -a -n "ERROR\|Exception\|error:" /home/dev/ff/configure3.log | tail -10
echo TRY3_DONE
