import io
p='/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/ets/GeckoViewBoot.ets'
s=io.open(p,encoding='utf-8').read()
if 'onTitle' not in s:
    a='  onIme?: (state: string) => void;'
    assert s.count(a)==1
    s=s.replace(a, a+"\n  onTitle?: (title: string, url: string, session: string) => void;")
    anchor='\n      if (handlers.onIme !== undefined) {\n        geckoview.registerIMECallback'
    assert s.count(anchor)==1, s.count(anchor)
    block="""      geckoview.registerTabStateCallback((json: string) => {
        try {
          const payload: TabTitlePayload = JSON.parse(json) as TabTitlePayload;
          const title: string = payload.title !== undefined ? payload.title : '';
          const url: string = payload.url !== undefined ? payload.url : '';
          const session: string = payload.session !== undefined ? payload.session : '';
          if (title.length === 0 && url.length === 0) {
            return;
          }
          hilog.info(DOMAIN, TAG, 'title session=%{public}s title=%{public}s', session, title);
          if (handlers.onTitle !== undefined) {
            handlers.onTitle(title, url, session);
          }
        } catch (error) {
          hilog.warn(DOMAIN, TAG, 'tab-state parse failed: %{public}s', JSON.stringify(error));
        }
      });
""" + '      if (handlers.onIme !== undefined) {\n        geckoview.registerIMECallback'
    s=s.replace(anchor, block, 1)
    b='/** Plain mirror of the native surface-size payload. */'
    assert s.count(b)==1
    s=s.replace(b, '''/** Envelope pushed by geckoview.js for active-tab title/url sync. */
export interface TabTitlePayload {
  session?: string;
  title?: string;
  url?: string;
}

''' + b)
    io.open(p,'w',encoding='utf-8').write(s)
print('GeckoViewBoot ok:', 'onTitle' in io.open(p,encoding='utf-8').read())
