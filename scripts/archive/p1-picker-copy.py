import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
old="""      const paths: Array<string> = new Array<string>();
      for (let i = 0; i < uris.length; i++) {
        paths.push(uris[i].startsWith('file://') ? uris[i].substring(7) : uris[i]);
      }"""
assert s.count(old)==1
new="""      const paths: Array<string> = new Array<string>();
      for (let i = 0; i < uris.length; i++) {
        // Picker grants a file://docs/... URI; copy it into the sandbox so
        // Gecko can InitWithNativePath on a real absolute path.
        const srcFd = p1fs.openSync(uris[i], p1fs.OpenMode.READ_ONLY);
        const dst: string = `${this.contextRef.cacheDir}/picked_${Date.now()}_${i}`;
        p1fs.copyFileSync(srcFd.fd, dst);
        p1fs.closeSync(srcFd);
        paths.push(dst);
      }"""
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('picker copy fix')
