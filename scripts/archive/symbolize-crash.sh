#!/bin/bash
set -u
L=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/libxul.so
echo "=== symbols for crash frames ==="
for off in 0x39d88e0 0x3a053b4 0x3a802b4 0x3a80690 0x842c9c0 0x842c248 0x842f218 0x842f8a4 0x84329c4; do
  echo "--- $off ---"
  /opt/ohos-sdk/native/llvm/bin/llvm-addr2line -e "$L" -f -C "$off" 2>/dev/null | head -2
done
