import io
# libxul gate via file
p='/home/dev/ff/gecko/dom/media/platforms/PDMFactory.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('''  if (Preferences::GetBool("media.ohos.hw_decode", true)) {''',
'''  if (access("/data/storage/el2/base/haps/entry/files/hwdecode.off",
             F_OK) != 0) {''')
io.open(p,'w',encoding='utf-8').write(s)
print('file gate:', 'hwdecode.off' in s)
