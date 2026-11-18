#!/bin/bash
cd /home/dev/ff/gecko
for opt in disable-perfetto disable-profiling disable-parental-controls disable-webrtc disable-accessibility disable-geckodriver disable-webcodecs disable-webgpu; do
  if grep -rq -- "--$opt" --include='*.configure' --include='moz.configure' . 2>/dev/null; then
    echo "FOUND --$opt"
  else
    echo "MISSING --$opt"
  fi
done
