import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
old="""        const dst: string = `${this.contextRef.cacheDir}/picked_${Date.now()}_${i}`;"""
assert s.count(old)==1
new="""        const base: string = uris[i].substring(uris[i].lastIndexOf('/') + 1);
        const dst: string = `${this.contextRef.cacheDir}/picked_${Date.now()}_${i}_${base}`;"""
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('basename preserved')
