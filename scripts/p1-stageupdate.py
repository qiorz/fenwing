import io
p='/mnt/d/ff-ohos/scripts/stage-hw-libxul.sh'
s=io.open(p,encoding='utf-8').read()
if 'libxul-hw-unstripped' not in s:
    s=s.replace('/opt/ohos-sdk/native/llvm/bin/llvm-strip --strip-unneeded "$L"',
                'cp -f "$L" /mnt/d/ff-ohos/artifacts/gecko/libxul-hw-unstripped.so\n/opt/ohos-sdk/native/llvm/bin/llvm-strip --strip-unneeded "$L"')
io.open(p,'w',encoding='utf-8').write(s)
print('stage script updated')
