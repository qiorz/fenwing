import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
if '<video id="v"' not in s:
    a="'<script>function dl()"
    assert s.count(a)==1, s.count(a)
    s=s.replace(a, "'<p><video id=\"v\" src=\"__VIDEO__\" autoplay loop muted playsinline controls width=\"640\" height=\"360\"></video></p>" + a)
    io.open(p,'w',encoding='utf-8').write(s)
print('video inserted:', '<video id="v"' in io.open(p,encoding='utf-8').read())
