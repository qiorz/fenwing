import io

p = '/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.h'
s = io.open(p, encoding='utf-8').read()
s = s.replace('  nsTArray<uint32_t> mFreeInputs;',
              '  struct FreeInputBuffer {\n    uint32_t mIndex;\n    OH_AVBuffer* mBuffer;\n  };\n  nsTArray<FreeInputBuffer> mFreeInputs;')
io.open(p, 'w', encoding='utf-8').write(s)

p = '/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s = io.open(p, encoding='utf-8').read()

s = s.replace('  self->mFreeInputs.AppendElement(aIndex);',
              '  self->mFreeInputs.AppendElement(FreeInputBuffer{aIndex, aBuffer});')

old = '''    uint32_t index = mFreeInputs[0];
    mFreeInputs.RemoveElementAt(0);
    OH_AVBuffer* buf = gApi.getInput(mCodec, index);
    if (!buf) {
      OHOS_HLOG("getInput null idx=%{public}d", (int)index);
      continue;
    }'''
new = '''    FreeInputBuffer input = mFreeInputs[0];
    mFreeInputs.RemoveElementAt(0);
    uint32_t index = input.mIndex;
    OH_AVBuffer* buf = input.mBuffer;
    if (!buf) {
      OHOS_HLOG("input buffer null idx=%{public}d", (int)index);
      continue;
    }'''
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('use callback-provided input buffers')
