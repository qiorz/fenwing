#!/bin/bash
set -u
cd /home/dev/ff/gecko/ports/ohos
for fn in GoBackForSession GoForwardForSession ReloadForSession StopForSession GetSessionHistory GoToIndexForSession; do
  ln=$(grep -n "napi_value $fn" geckoview.cpp | head -1 | cut -d: -f1)
  echo "--- $fn (line $ln) ---"
  [ -n "${ln:-}" ] && sed -n "${ln},$((ln+38))p" geckoview.cpp
done
