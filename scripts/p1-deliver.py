import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'IMMEDIATE' not in s:
    s=s.replace('    OHOS_HLOG("decode immediate frames=%{public}d", (int)frames.Length());',
                '    OHOS_HLOG("decode immediate frames=%{public}d", (int)frames.Length());\n    OHOSMarker("IMMEDIATE");')
    s=s.replace('  if (ready.Length() > 0) { OHOSMarker("RESOLVE_FRAMES"); }',
                '  if (ready.Length() > 0) { OHOSMarker("RESOLVE_FRAMES"); }')
    s=s.replace('  OHOS_HLOG("queued frames=%{public}d", (int)frames.Length());',
                '  OHOS_HLOG("queued frames=%{public}d", (int)frames.Length());\n  OHOSMarker("QUEUED");')
io.open(p,'w',encoding='utf-8').write(s)
print('delivery markers:', all(k in s for k in ('IMMEDIATE','RESOLVE_FRAMES','QUEUED')))
