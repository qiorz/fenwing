#!/bin/bash
set -u
FP=/home/dev/ff/gecko/widget/openharmony/OHOSFilePicker.cpp
MB=/home/dev/ff/gecko/widget/openharmony/OHOSMenuBridge.cpp
echo "=== FilePicker JSON keys ==="
grep -n 'AppendLiteral\|Append(' "$FP" | head -40
echo
echo "=== Menu JSON keys ==="
grep -n 'AppendLiteral\|Append(' "$MB" | head -80
