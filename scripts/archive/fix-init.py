import io
p='/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/ets/GeckoViewBoot.ets'
s=io.open(p,encoding='utf-8').read()
old="""      uiMode: 'classic'
    });

  static loadUrl"""
assert s.count(old)==1, s.count(old)
s=s.replace(old,"""      uiMode: 'classic'
    });
    hilog.info(DOMAIN, TAG, 'initFirefox dispatched');
  }

  static loadUrl""")
io.open(p,'w',encoding='utf-8').write(s)
print('fixed init closing')
