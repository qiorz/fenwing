import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'OHOSMarker("QUEUED")' not in s:
    s=s.replace('  mFrames.AppendElement(video);',
                '  mFrames.AppendElement(video);\n  OHOSMarker("QUEUED");')
io.open(p,'w',encoding='utf-8').write(s)
print('queued marker:', 'OHOSMarker("QUEUED")' in s)
