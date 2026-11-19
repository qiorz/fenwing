#!/bin/bash
set -eu
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
export PATH=/opt/ohos-sdk/native/llvm/bin:$PATH
export MOZ_OBJDIR=/home/dev/ff/gecko/obj-hw
cd /home/dev/ff/gecko
exec ./mach build > /home/dev/ff/gecko-hw.log 2>&1
