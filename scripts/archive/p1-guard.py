import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
a="""  private async openFilePicker(callbackId: number, req: PickerRequest): Promise<void> {
    try {"""
assert s.count(a)==1
s=s.replace(a,"""  private async openFilePicker(callbackId: number, req: PickerRequest): Promise<void> {
    if (this.contextRef === undefined) {
      GeckoViewBoot.resolveFilePicker(callbackId, 1, '');
      return;
    }
    try {""")
b="""  private onFullscreenChanged(): void {
    try {"""
assert s.count(b)==1
s=s.replace(b,"""  private onFullscreenChanged(): void {
    if (this.contextRef === undefined) {
      return;
    }
    try {""")
io.open(p,'w',encoding='utf-8').write(s)
print('context guards added')
