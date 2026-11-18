#!/bin/bash
set -u
cd /home/dev/ff/gecko/ports/ohos
echo "=== input napi functions ==="
grep -n 'napi_value TouchEvent\|napi_value MouseMove\|napi_value MouseDown\|napi_value MouseUp\|napi_value Scroll\|napi_value DispatchKeyEventNapi\|napi_value InsertText\|napi_value DeleteText\|napi_value RegisterIMECallback' geckoview.cpp
echo
echo "=== TouchEvent body ==="
ln=$(grep -n 'napi_value TouchEvent' geckoview.cpp | head -1 | cut -d: -f1)
sed -n "${ln},$((ln+60))p" geckoview.cpp
echo
echo "=== MouseMove body ==="
ln=$(grep -n 'napi_value MouseMove' geckoview.cpp | head -1 | cut -d: -f1)
sed -n "${ln},$((ln+45))p" geckoview.cpp
