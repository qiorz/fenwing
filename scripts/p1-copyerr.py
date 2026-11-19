import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'createAndCopy' not in s:
    s=s.replace('  if (result.isErr()) {\n    return;\n  }',
'''  if (result.isErr()) {
    OHOS_HLOG("createAndCopy failed code=%{public}u", (unsigned)result.inspectErr().Code());
    return;
  }''')
    s=s.replace('  RefPtr<VideoData> video = result.unwrap();\n  if (!video) {\n    return;\n  }',
'''  RefPtr<VideoData> video = result.unwrap();
  if (!video) {
    OHOS_HLOG("video null");
    return;
  }''')
io.open(p,'w',encoding='utf-8').write(s)
print('createAndCopy diagnostics added')
