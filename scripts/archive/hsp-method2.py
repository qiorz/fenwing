import zipfile
p='/mnt/d/ff-ohos/work/firefoxport/gecko/build/default/outputs/default/gecko-default-signed.hsp'
z=zipfile.ZipFile(p)
n=0
for x in z.namelist():
    if 'libxul' in x or x.endswith('omni.ja'):
        i=z.getinfo(x); print(x, i.file_size, i.compress_type); n+=1
print('total entries', len(z.namelist()))
