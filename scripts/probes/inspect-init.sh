#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== InitFirefox definition / init flow ==="
grep -n 'napi_value InitFirefox\|InitFirefox(' ports/ohos/geckoview.cpp | head
echo
echo "=== resourceDir / omni / profile handling ==="
grep -n 'resourceDir\|omni\|GRE_DIR\|XRE_InitEmbedding\|XRE_main\|XRE_GetBootstrap\|ARGS' ports/ohos/geckoview.cpp | head -40
echo
echo "=== chrome bridge / mandatory ArkTS registration ==="
grep -n 'OHOSChromeBridge\|ChromeBridge_\|RegisterChrome\|chromeBridge' ports/ohos/geckoview.cpp | head -20
echo
echo "=== InitFirefox body (first 140 lines after definition) ==="
ln=$(grep -n 'napi_value InitFirefox' ports/ohos/geckoview.cpp | head -1 | cut -d: -f1)
sed -n "${ln},$((ln+150))p" ports/ohos/geckoview.cpp
