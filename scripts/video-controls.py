import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
s=s.replace('autoplay loop muted playsinline width="640"','autoplay loop muted playsinline controls width="640" height="360"')
s=s.replace('</video></p>','</video></p><p><button onclick="document.getElementById(\'v\').play()" style="font-size:22px;padding:12px">播放视频</button></p>')
io.open(p,'w',encoding='utf-8').write(s)
print('video controls added', '播放视频' in s)
