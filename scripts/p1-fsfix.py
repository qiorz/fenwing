import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
s=s.replace('const f = fileIo.openSync(flag, fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY);\n        fileIo.closeSync(f);',
            'const f = fs.openSync(flag, fs.OpenMode.CREATE | fs.OpenMode.WRITE_ONLY);\n        fs.closeSync(f);')
s=s.replace('fileIo.unlinkSync(flag);','fs.unlinkSync(flag);')
io.open(p,'w',encoding='utf-8').write(s)
print('fs alias fixed:', 'fileIo.' not in s)
