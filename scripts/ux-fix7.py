import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
# restore first occurrence (DB init) only
i=s.find('设置读取失败')
s=s[:i]+s[i:].replace('设置读取失败','数据库初始化失败',1)
io.open(p,'w',encoding='utf-8').write(s)
print('db string restored')
