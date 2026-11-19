import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('  if (decNo % 30 == 0) { OHOS_HLOG("decode #%{public}d", decNo); }',
            '  if (decNo < 12) { OHOS_HLOG("decode #%{public}d size=%{public}d", decNo, (int)aSample->Size()); }')
s=s.replace('        OHOS_HLOG("push input idx=%{public}d size=%{public}d", (int)index, (int)attr.size);',
            '        OHOS_HLOG("push input idx=%{public}d size=%{public}d", (int)index, (int)attr.size);')
s=s.replace('  int outNo = sOut.fetch_add(1);',
            '  int outNo = sOut.fetch_add(1);\n  if (outNo < 12) { OHOS_HLOG("output cb #%{public}d", outNo); }')
io.open(p,'w',encoding='utf-8').write(s)
print('verbose early logs')
