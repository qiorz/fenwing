#!/bin/bash
L=/opt/ohos-sdk/native/sysroot/usr/lib/aarch64-linux-ohos
for f in libnative_media_vdec.so libnative_media_codecbase.so libnative_media_core.so; do
  echo "== $f"
  for s in OH_VideoDecoder_Flush OH_VideoDecoder_PushInputBuffer OH_AVBuffer_GetCapacity OH_AVBuffer_GetBufferAttr OH_VideoDecoder_CreateByMime; do
    c=$(nm -D "$L/$f" 2>/dev/null | grep -c "$s")
    echo "  $s: $c"
  done
done
