import zipfile
p='D:/ff-ohos/work/firefoxport/gecko/build/default/outputs/default/gecko-default-signed.hsp'
z=zipfile.ZipFile(p)
for n in z.namelist():
    if 'libxul' in n or n.endswith('omni.ja') or n.endswith('.so'):
        i=z.getinfo(n)
        print(n, i.file_size, i.compress_type)
