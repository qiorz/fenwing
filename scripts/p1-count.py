import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('  OHOS_HLOG("decode call size=%{public}d", (int)aSample->Size());',
            '  OHOS_HLOG("decode call size=%{public}d", (int)aSample->Size());')
s=s.replace('  OHOS_HLOG("decode promise created pending=%{public}d", mPendingSample ? 1 : 0);',
            '  OHOS_HLOG("decode promise created pending=%{public}d free=%{public}d", mPendingSample ? 1 : 0, (int)mFreeInputs.Length());')
s=s.replace('        OHOS_HLOG("push input size=%{public}d", (int)attr.size);',
            '        OHOS_HLOG("push input idx=%{public}d size=%{public}d", (int)index, (int)attr.size);')
s=s.replace('  static std::atomic<int> sOut{0};\n  if (sOut.fetch_add(1) == 0) {',
            '  static std::atomic<int> sOut{0};\n  int outNo = sOut.fetch_add(1);\n  if (outNo < 5) { OHOS_HLOG("output #%{public}d pts=%{public}lld", outNo, (long long)attr.pts); }\n  if (outNo == 0) {')
io.open(p,'w',encoding='utf-8').write(s)
print('decode/push counters added')
