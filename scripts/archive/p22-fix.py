import io
p='/mnt/d/ff-ohos/scripts/p22-browserpage.py'
s=io.open(p,encoding='utf-8').read()
s=s.replace('rep("  private cancelDownload(id: string): void {",','rep("  private async cancelDownload(id: string): Promise<void> {",')
io.open(p,'w',encoding='utf-8').write(s)
print('anchor fixed')
