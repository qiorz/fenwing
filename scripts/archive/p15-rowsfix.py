import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
old="hilog.info(DOMAIN, TAG, 'menu shown id=%{public}d rows=%{public}d', this.menuId, rows.length);"
assert s.count(old)==1
s=s.replace(old,"hilog.info(DOMAIN, TAG, 'menu shown id=%{public}d rows=%{public}d', this.menuId, this.menuRows.length);")
io.open(p,'w',encoding='utf-8').write(s)
print('rows ref fixed')
