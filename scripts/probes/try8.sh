#!/bin/bash
# try8.sh — 首版关闭 wasm sandbox（无 wasi sysroot），重跑 configure
set -u
cd /home/dev/ff/gecko
export PATH="/opt/ohos-sdk/native/llvm/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export MOZBUILD_STATE_PATH="$HOME/.mozbuild"
export RUSTUP_TOOLCHAIN=stable

cat > ./mozconfig <<'EOF'
ac_add_options --enable-application=mobile/ohos
ac_add_options --target=aarch64-unknown-linux-ohos
ac_add_options --host=x86_64-unknown-linux-gnu
ac_add_options --disable-bootstrap
ac_add_options --disable-jemalloc
ac_add_options --without-wasm-sandboxed-libraries
ac_add_options --enable-optimize
ac_add_options --disable-debug
ac_add_options --disable-tests
ac_add_options --disable-updater
ac_add_options --disable-crashreporter
EOF

./mach --no-interactive configure > /home/dev/ff/configure8.log 2>&1
rc=$?
echo "CONFIGURE_RC=$rc"
tail -20 /home/dev/ff/configure8.log
echo "=== error lines ==="
grep -a -n "ERROR\|Exception\|error:" /home/dev/ff/configure8.log | tail -8
echo TRY8_DONE
