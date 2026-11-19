import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
if 'video' not in s:
    a='<p><a href="https://example.com/">示例链接</a></p>'
    assert s.count(a)==1
    s=s.replace(a, a+'<p><video id="v" src="https://www.w3schools.com/html/mov_bbb.mp4" autoplay loop muted playsinline width="640"></video></p>')
    io.open(p,'w',encoding='utf-8').write(s)
print('video tag added')
