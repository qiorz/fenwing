#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P0: wire crash marker + session store + optional url launch param."""
import io

ROOT = '/mnt/d/ff-ohos/work/firefoxport'
p = ROOT + '/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()

if 'SessionStore' not in s:
    s = s.replace("import { GeckoViewBoot, GeckoViewHandlers } from 'gecko';",
                  "import { GeckoViewBoot, GeckoViewHandlers } from 'gecko';\nimport { SessionStore } from '../service/SessionStore';", 1)

    # configure store + unclean detection before boot
    old = "    const perf: boolean = this.paramIsOne(want, 'perf');\n    const nojit: boolean = this.paramIsOne(want, 'nojit');"
    assert s.count(old) == 1
    s = s.replace(old, """    const perf: boolean = this.paramIsOne(want, 'perf');
    const nojit: boolean = this.paramIsOne(want, 'nojit');
    const store: SessionStore = SessionStore.instance();
    store.configure(this.context.filesDir);
    const unclean: boolean = store.beginEngineRun();
    AppStorage.setOrCreate('engineUnclean', unclean);
    hilog.info(DOMAIN, 'GeckoBoot', 'previous run unclean=%{public}s', `${unclean}`);""")

    # optional url parameter
    old2 = "    this.bootGecko(perf, nojit);"
    assert s.count(old2) == 1
    s = s.replace(old2, "    this.bootGecko(perf, nojit, this.stringParam(want, 'url'));")
    s = s.replace("  private bootGecko(perf: boolean, nojit: boolean): void {",
                  "  private bootGecko(perf: boolean, nojit: boolean, overrideUrl: string): void {", 1)

    old3 = "      let startUrl: string = 'https://example.com/';"
    assert s.count(old3) == 1
    s = s.replace(old3, """      let startUrl: string = 'https://example.com/';
      if (overrideUrl.length > 0) {
        startUrl = overrideUrl;
        hilog.info(DOMAIN, 'GeckoBoot', 'url override: %{public}s', startUrl);
      }""")

    # graceful exit marker cleanup
    old4 = "  onDestroy(): void {\n    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onDestroy');\n  }"
    assert s.count(old4) == 1, s.count(old4)
    s = s.replace(old4, """  onDestroy(): void {
    SessionStore.instance().endEngineRun();
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onDestroy (clean exit marker cleared)');
  }""")

    # stringParam helper next to paramIsOne
    anchor = "  private paramIsOne(want: Want, key: string): boolean {"
    assert s.count(anchor) == 1
    s = s.replace(anchor, """  private stringParam(want: Want, key: string): string {
    try {
      const params: Record<string, Object> | undefined = want.parameters;
      if (params === undefined) {
        return '';
      }
      const value: Object | undefined = params[key];
      return value !== undefined ? value.toString() : '';
    } catch (error) {
      return '';
    }
  }

""" + anchor)

io.open(p, 'w', encoding='utf-8').write(s)
print('EntryAbility P0 wired')
