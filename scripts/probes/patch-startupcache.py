#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add startupCache cleanup before engine boot in EntryAbility.ets."""
import io

p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
src = io.open(p, encoding='utf-8').read()

anchor = "      GeckoViewBoot.init('https://example.com/', dir);"
if 'clearStartupCache' not in src:
    assert src.count(anchor) == 1, src.count(anchor)
    src = src.replace(anchor,
        "      this.clearStartupCache(`${this.context.filesDir}/profile`);\n"
        "      GeckoViewBoot.init('https://example.com/', dir);")

tail_anchor = "\n  }\n}\n"
idx = src.rfind(tail_anchor)
assert idx > 0, 'class tail not found'
helpers = """
  }

  /**
   * Gecko caches compiled chrome scripts in <profile>/startupCache. That cache
   * survives app reinstall/rebuild, so edited omni.ja JS would be ignored.
   * Clearing it before XRE_main forces chrome scripts to be re-read from the
   * freshly unpacked omni.ja.
   */
  private clearStartupCache(profileDir: string): void {
    const cacheDir = profileDir + '/startupCache';
    try {
      if (fs.accessSync(cacheDir)) {
        this.removeDirRecursive(cacheDir);
        hilog.info(DOMAIN, 'GeckoBoot', 'startupCache cleared');
      }
    } catch (error) {
      hilog.warn(DOMAIN, 'GeckoBoot', 'startupCache cleanup failed: %{public}s', JSON.stringify(error));
    }
  }

  private removeDirRecursive(dir: string): void {
    const names: string[] = fs.listFileSync(dir);
    for (const name of names) {
      const child = dir + '/' + name;
      if (fs.statSync(child).isDirectory()) {
        this.removeDirRecursive(child);
      } else {
        fs.unlinkSync(child);
      }
    }
    fs.rmdirSync(dir);
  }
}
"""
if 'clearStartupCache(profileDir' not in src:
    src = src[:idx] + helpers + src[idx + len(tail_anchor):]
io.open(p, 'w', encoding='utf-8').write(src)
print('OK startupCache cleanup added; size', len(src))
