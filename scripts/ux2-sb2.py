import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
s=s.replace(".width(6)\n              .height(Math.max(40,", ".width(8)\n              .height(Math.max(40,")
s=s.replace(".backgroundColor('#88A8C8FF')", ".backgroundColor('#FF5B9BFF')")
s=s.replace("          }, 1500);", "          }, 3000);")
io.open(p,'w',encoding='utf-8').write(s)
print('scrollbar style bumped')
