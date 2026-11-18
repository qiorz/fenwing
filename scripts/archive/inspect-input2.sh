#!/bin/bash
set -u
cd /home/dev/ff/gecko/ports/ohos
echo "=== Scroll ==="
ln=$(grep -n 'napi_value Scroll' geckoview.cpp | head -1 | cut -d: -f1); sed -n "${ln},$((ln+30))p" geckoview.cpp
echo "=== DispatchKeyEventNapi ==="
ln=$(grep -n 'napi_value DispatchKeyEventNapi' geckoview.cpp | head -1 | cut -d: -f1); sed -n "${ln},$((ln+35))p" geckoview.cpp
echo "=== InsertText / DeleteText ==="
ln=$(grep -n 'napi_value InsertText' geckoview.cpp | head -1 | cut -d: -f1); sed -n "${ln},$((ln+60))p" geckoview.cpp
echo "=== RegisterIMECallback ==="
ln=$(grep -n 'napi_value RegisterIMECallback' geckoview.cpp | head -1 | cut -d: -f1); sed -n "${ln},$((ln+40))p" geckoview.cpp
