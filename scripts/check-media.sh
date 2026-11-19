#!/bin/bash
cd /home/dev/ff/gecko
echo "=== OH_AVCodec / AVCodec usage ==="
grep -rln 'OH_AVCodec\|OH_VideoDecoder\|OH_AVSource' --include=*.cpp --include=*.h dom/media widget/openharmony media 2>/dev/null | head -20
echo "=== ohos media decoder platform ==="
ls dom/media/platforms 2>/dev/null | head
echo "=== port media files ==="
find widget/openharmony dom/media -iname '*ohos*' 2>/dev/null | head -20
echo "=== mozconfig media flags ==="
grep -iE 'media|ffmpeg|av1|vpx|openharmony' mozconfig 2>/dev/null
