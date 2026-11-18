import io
# JS: filename from data URI mime
p='/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js'
s=io.open(p,encoding='utf-8').read()
old="""            const a = doc.createElement("a");
            a.href = img.src;
            a.download = (img.src.split("/").pop() || "image");"""
assert s.count(old)==1
new="""            let name = "image";
            try {
              if (img.src.startsWith("data:")) {
                const mime = img.src.substring(5, img.src.indexOf(";") > 0 ? img.src.indexOf(";") : img.src.indexOf(","));
                const ext = mime.indexOf("svg") >= 0 ? "svg" : (mime.indexOf("png") >= 0 ? "png" : (mime.indexOf("jpeg") >= 0 || mime.indexOf("jpg") >= 0 ? "jpg" : "bin"));
                name = "image." + ext;
              } else {
                name = (img.src.split("/").pop() || "image");
              }
            } catch (e) {}
            const a = doc.createElement("a");
            a.href = img.src;
            a.download = name;"""
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('img filename fixed')

# ArkTS: mime by extension
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
old="""      const uri: string = fileUri.getUriFromPath(path);
      this.contextRef.startAbility({
        action: 'ohos.want.action.viewData',
        uri: uri,
        type: 'text/plain'
      }).catch((error: Object) => {"""
assert s.count(old)==1
new="""      const uri: string = fileUri.getUriFromPath(path);
      let mime: string = '*/*';
      const lower: string = path.toLowerCase();
      if (lower.endsWith('.svg')) {
        mime = 'image/svg+xml';
      } else if (lower.endsWith('.png')) {
        mime = 'image/png';
      } else if (lower.endsWith('.jpg') || lower.endsWith('.jpeg')) {
        mime = 'image/jpeg';
      } else if (lower.endsWith('.txt')) {
        mime = 'text/plain';
      } else if (lower.endsWith('.pdf')) {
        mime = 'application/pdf';
      }
      this.contextRef.startAbility({
        action: 'ohos.want.action.viewData',
        uri: uri,
        type: mime
      }).catch((error: Object) => {"""
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('mime mapping added')
