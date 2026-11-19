import io
p='/home/dev/ff/gecko/dom/media/platforms/moz.build'
s=io.open(p,encoding='utf-8').read()
old='if CONFIG["MOZ_WIDGET_OPENHARMONY"]:\n    DIRS += ["ohos"]'
assert s.count(old)==1
s=s.replace(old,'DIRS += ["ohos"]')
io.open(p,'w',encoding='utf-8').write(s)
print('DIRS unconditional now')
