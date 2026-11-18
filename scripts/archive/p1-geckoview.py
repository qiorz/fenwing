#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1 host wiring: downloads, file picker, fullscreen, find-in-page, zoom."""
import io

ROOT = '/mnt/d/ff-ohos/work/firefoxport'

# ---------------------------------------------------------------- GeckoViewBoot
p = ROOT + '/gecko/src/main/ets/GeckoViewBoot.ets'
s = io.open(p, encoding='utf-8').read()

if 'registerDownload' not in s:
    # handlers
    a = "  onTitle?: (title: string, url: string, session: string) => void;"
    assert s.count(a) == 1
    s = s.replace(a, a + """
  onDownload?: (json: string) => void;
  onFilePicker?: (json: string, callbackId: number) => void;
  onFullscreen?: (fullscreen: boolean) => void;""")

    # registrations
    a = "      hilog.info(DOMAIN, TAG, 'callbacks registered');"
    assert s.count(a) == 1
    s = s.replace(a, """      if (handlers.onDownload !== undefined) {
        geckoview.registerDownloadCallback((json: string) => {
          if (handlers.onDownload !== undefined) {
            handlers.onDownload(json);
          }
        });
      }
      if (handlers.onFilePicker !== undefined) {
        geckoview.registerFilePickerCallback((json: string, callbackId: number) => {
          if (handlers.onFilePicker !== undefined) {
            handlers.onFilePicker(json, callbackId);
          }
        });
      }
      if (handlers.onFullscreen !== undefined) {
        geckoview.registerFullscreenCallback((fullscreen: boolean) => {
          if (handlers.onFullscreen !== undefined) {
            handlers.onFullscreen(fullscreen);
          }
        });
      }
""" + a)

    # public methods before class end
    a = """  static deleteText(length: number): void {
    geckoview.deleteText(length);
  }
}"""
    assert s.count(a) == 1
    s = s.replace(a, """  static deleteText(length: number): void {
    geckoview.deleteText(length);
  }

  static resolveFilePicker(callbackId: number, result: number, path: string): void {
    hilog.info(DOMAIN, TAG, 'resolveFilePicker id=%{public}d result=%{public}d', callbackId, result);
    geckoview.resolveFilePicker(callbackId, result, path);
  }

  static exitFullscreen(): void {
    geckoview.exitFullscreen();
  }

  static findInPage(query: string, backward: boolean, matchCase: boolean): void {
    hilog.info(DOMAIN, TAG, 'findInPage %{public}s', query);
    geckoview.findInPage(query, backward ? 1 : 0, matchCase ? 1 : 0);
  }

  static setFullZoom(zoom: number): void {
    hilog.info(DOMAIN, TAG, 'setFullZoom %{public}f', zoom);
    geckoview.setFullZoom(zoom);
  }
}""")
    io.open(p, 'w', encoding='utf-8').write(s)
print('GeckoViewBoot P1 methods ok')

# ---------------------------------------------------------------- d.ts
p = ROOT + '/gecko/src/main/cpp/types/libgeckoview/index.d.ts'
s = io.open(p, encoding='utf-8').read()
if 'registerDownloadCallback' not in s:
    a = "export const registerTabStateCallback: (callback: (json: string) => void) => void;"
    assert s.count(a) == 1
    s = s.replace(a, a + """
export const registerDownloadCallback: (callback: (json: string) => void) => void;
export const registerFilePickerCallback: (callback: (json: string, callbackId: number) => void) => void;
export const registerFullscreenCallback: (callback: (fullscreen: boolean) => void) => void;
export const resolveFilePicker: (callbackId: number, result: number, path: string) => void;
export const exitFullscreen: () => void;
export const findInPage: (query: string, backward: number, matchCase: number) => void;
export const setFullZoom: (zoom: number) => void;""")
    io.open(p, 'w', encoding='utf-8').write(s)
print('d.ts P1 ok')

# ---------------------------------------------------------------- EntryAbility handlers
p = ROOT + '/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()
if 'onDownload' not in s:
    a = """        onTitle: (title: string, url: string, session: string) => {"""
    assert s.count(a) == 1
    s = s.replace(a, """        onDownload: (json: string) => {
          AppStorage.setOrCreate('geckoDownload', json);
        },
        onFilePicker: (json: string, callbackId: number) => {
          AppStorage.setOrCreate('geckoFilePicker', JSON.stringify({ id: callbackId, req: json }));
        },
        onFullscreen: (fullscreen: boolean) => {
          AppStorage.setOrCreate('geckoFullscreen', fullscreen);
        },
""" + a)
    io.open(p, 'w', encoding='utf-8').write(s)
print('EntryAbility P1 handlers ok')
