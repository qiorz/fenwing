import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
s=s.replace("import { SavedSession, SessionStore } from '../service/SessionStore';","import { SavedSession, SavedTab, SessionStore } from '../service/SessionStore';")
io.open(p,'w',encoding='utf-8').write(s)
print('import fixed')
