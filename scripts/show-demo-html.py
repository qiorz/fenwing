import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
i=s.find('const DEMO_PAGE_HTML')
print(repr(s[i:i+80]))
print('---tail---')
print(repr(s[i+1000:i+1900]))
