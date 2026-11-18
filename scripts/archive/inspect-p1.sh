#!/bin/bash
set -u
cd /home/dev/ff/gecko/ports/ohos
for fn in RegisterDownloadCallback RegisterFilePickerCallback ResolveFilePicker RegisterFullscreenCallback RegisterMenuCallback ResolveMenuCommand CloseNativeMenu FindInPage SetFullZoom; do
  ln=$(grep -n "napi_value $fn" geckoview.cpp | head -1 | cut -d: -f1)
  echo "===== $fn (line $ln) ====="
  [ -n "${ln:-}" ] && sed -n "${ln},$((ln+32))p" geckoview.cpp
done
echo "===== download bridge headers ====="
grep -n 'OHOSDownloadBridge\|DownloadEvent\|download' geckoview.cpp | head -20
