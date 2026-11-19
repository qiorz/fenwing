import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
s=s.replace("'gecko_xre_diag.txt', 'gecko_debug.txt', 'gecko_nspr.txt'", "'gecko_xre_diag.txt', 'gecko_debug.txt', 'gecko_nspr.txt', 'ohosdec.log'")
io.open(p,'w',encoding='utf-8').write(s)
print('diag list updated')
