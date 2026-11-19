import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()

# field
a="  @State private recoveredCount: number = 0;"
assert s.count(a)==1
if 'recoveredLastUrl' not in s:
    s=s.replace(a, a+"\n  @State private recoveredLastUrl: string = '';")

# unclean block: add last url
a="""        this.recoveredCount = saved.tabs.length;
        this.showRecoveryBanner = true;"""
assert s.count(a)==1
new="""        this.recoveredCount = saved.tabs.length;
        const lastIdx: number = Math.min(Math.max(saved.activeIndex, 0), saved.tabs.length - 1);
        this.recoveredLastUrl = saved.tabs[lastIdx].url;
        this.showRecoveryBanner = true;"""
s=s.replace(a,new)

# log line with last url
a="""        hilog.warn(DOMAIN, TAG, 'unclean exit detected, restored %{public}d tabs', saved.tabs.length);"""
assert s.count(a)==1
s=s.replace(a,"""        hilog.warn(DOMAIN, TAG, 'unclean exit detected, restored %{public}d tabs, last=%{public}s',
          saved.tabs.length, this.recoveredLastUrl);""")

# banner text include last url
a="""          Text(`检测到上次异常退出，已自动恢复 ${this.recoveredCount} 个标签`)"""
assert s.count(a)==1
s=s.replace(a,"""          Text(`检测到上次异常退出，已自动恢复 ${this.recoveredCount} 个标签${this.recoveredLastUrl.length > 0 ? '（上次停留：' + (this.recoveredLastUrl.length > 40 ? this.recoveredLastUrl.substring(0, 40) + '…' : this.recoveredLastUrl) + '）' : ''}`)""")
io.open(p,'w',encoding='utf-8').write(s)
print('crash context banner upgraded')
