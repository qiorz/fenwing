#!/bin/bash
set -u
I=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/include
ls -l "$I/mozilla/Bootstrap.h" "$I/mozilla-config.h" 2>&1
echo "=== class Bootstrap public API ==="
grep -n 'class Bootstrap\|struct BootstrapConfig\|UniquePtr\|GetBuildID\|GetAppData\|XRE_GetBootstrap' "$I/mozilla/Bootstrap.h" | head -30
echo
echo "=== first 80 lines ==="
sed -n '1,80p' "$I/mozilla/Bootstrap.h"
