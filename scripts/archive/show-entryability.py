import io
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()
print('len', len(s))
i = s.find('class EntryAbility')
print(repr(s[max(0, i-400):i+120]))
print('BENCH count', s.count('BENCH'))
print('init lines:')
for line in s.splitlines():
    if 'GeckoViewBoot.init' in line:
        print(repr(line[:160]))
