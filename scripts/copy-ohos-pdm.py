import os, shutil
src='/mnt/d/ff-ohos/work/firefoxport/third_party/gecko/dom/media/platforms/ohos'
dst='/home/dev/ff/gecko/dom/media/platforms/ohos'
os.makedirs(dst, exist_ok=True)
for f in os.listdir(src):
    shutil.copy2(os.path.join(src,f), os.path.join(dst,f))
    print('copied', f)
