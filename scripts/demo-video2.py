import io, shutil, os
R='/mnt/d/ff-ohos/work/firefoxport'
# copy video into rawfile
dst=R+'/entry/src/main/resources/rawfile/test720.mp4'
shutil.copy2('/mnt/d/ff-ohos/artifacts/test720.mp4', dst)
print('video copied', os.path.getsize(dst))
p=R+'/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
s=s.replace('src="https://www.w3schools.com/html/mov_bbb.mp4"', 'src="__VIDEO__"')
old="""      if (demo) {
        const demoPath: string = this.context.filesDir + '/demo.html';"""
assert s.count(old)==1
s=s.replace(old,"""      if (demo) {
        // copy bundled test clip so the demo page has a local H.264 source
        const clipPath: string = this.context.filesDir + '/test720.mp4';
        try {
          const clip: Uint8Array = this.context.resourceManager.getRawFileContentSync('test720.mp4');
          const fd = fs.openSync(clipPath, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);
          fs.writeSync(fd.fd, clip.buffer);
          fs.closeSync(fd);
        } catch (clipError) {
          hilog.warn(DOMAIN, 'GeckoBoot', 'clip copy failed');
        }
        const demoHtml: string = DEMO_PAGE_HTML.replace('__VIDEO__', 'file://' + clipPath);
        const demoPath: string = this.context.filesDir + '/demo.html';""")
s=s.replace("fs.writeSync(demoFd.fd, DEMO_PAGE_HTML);", "fs.writeSync(demoFd.fd, demoHtml);")
io.open(p,'w',encoding='utf-8').write(s)
print('demo video wired')
