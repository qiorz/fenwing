#!/bin/bash
set -u
sed -n '150,190p' /home/dev/ff/gecko/widget/openharmony/OHOSFilePicker.cpp
echo "=== menu json keys ==="
grep -n 'menuId\|anchorRect\|items\|JSONWriter\|ToJSON\|append' /home/dev/ff/gecko/widget/openharmony/OHOSMenuBridge.cpp | head -30
