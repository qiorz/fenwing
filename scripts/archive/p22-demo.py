import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
old='<p><input type="file"'
assert s.count(old)==1
s=s.replace(old,'<p><a href="https://example.com/">示例链接</a></p><p><input type="file"')
io.open(p,'w',encoding='utf-8').write(s)
print('demo link restored')
