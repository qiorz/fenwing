import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('  OHOS_HLOG("needInput idx=%d", (int)aIndex);','  OHOS_HLOG("needInput idx=%{public}d", (int)aIndex);')
s=s.replace('  while (!mFreeInputs.IsEmpty() && (mPendingSample || mEOS)) {',
'''  OHOS_HLOG("tryPush free=%{public}d pending=%{public}d eos=%{public}d",
            (int)mFreeInputs.Length(), mPendingSample ? 1 : 0, mEOS ? 1 : 0);
  while (!mFreeInputs.IsEmpty() && (mPendingSample || mEOS)) {''')
s=s.replace('    OH_AVBuffer* buf = gApi.getInput(mCodec, index);\n    if (!buf) {\n      continue;\n    }',
'''    OH_AVBuffer* buf = gApi.getInput(mCodec, index);
    if (!buf) {
      OHOS_HLOG("getInput null idx=%{public}d", (int)index);
      continue;
    }''')
s=s.replace('      if (addr && cap > 0 && sample->Size() <= (size_t)cap) {',
'''      OHOS_HLOG("push attempt addr=%{public}p cap=%{public}d size=%{public}d",
                (void*)addr, (int)cap, (int)sample->Size());
      if (addr && cap > 0 && sample->Size() <= (size_t)cap) {''')
s=s.replace('        OHOS_HLOG("push input size=%d", (int)attr.size);','        OHOS_HLOG("push input size=%{public}d", (int)attr.size);')
s=s.replace('  OHOS_HLOG("decode call size=%d", (int)aSample->Size());','  OHOS_HLOG("decode call size=%{public}d", (int)aSample->Size());')
io.open(p,'w',encoding='utf-8').write(s)
print('input diagnostics added')
