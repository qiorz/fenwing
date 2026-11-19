import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
old='''  { static int s0 = 0; if (s0++ < 3) { OHOSPtrTag("OUTPUT", self, (int)aIndex, 0); } }
    return;
  }
'''
assert s.count(old)==1
s=s.replace(old,'''  { static int s0 = 0; if (s0++ < 3) { OHOSPtrTag("OUTPUT", self, (int)aIndex, 0); } }
''')
io.open(p,'w',encoding='utf-8').write(s)
print('fixed stray brace')
