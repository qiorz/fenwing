#!/bin/bash
D=/opt/ohos-sdk/native/sysroot/usr/lib/aarch64-linux-ohos
for f in "$D"/*.so; do
  if nm -D "$f" 2>/dev/null | grep -q 'OH_AVCodec_GetCapabilityList'; then
    echo "FOUND $f"
  fi
done
echo "--- headers ---"
grep -n 'OH_AVCODEC_TYPE_VIDEO_DECODER\|OH_AVCODEC_TYPE' /opt/ohos-sdk/native/sysroot/usr/include/multimedia/player_framework/native_avcapability.h | head
grep -n 'GetVideoWidthRange\b\|GetVideoHeightRange\b\|GetVideoWidthRangeForHeight\|GetSupportedLevels\|GetVideoSupportedFrameRateRanges' /opt/ohos-sdk/native/sysroot/usr/include/multimedia/player_framework/native_avcapability.h | head -20
