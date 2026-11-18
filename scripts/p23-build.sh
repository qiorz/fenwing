#!/bin/bash
set -eu
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export PATH=/opt/ohos-sdk/native/llvm/bin:$PATH
cd /home/dev/ff/gecko
exec ./mach build > /home/dev/ff/gecko-p23.log 2>&1
