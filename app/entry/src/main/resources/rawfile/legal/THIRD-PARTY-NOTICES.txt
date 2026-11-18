# THIRD-PARTY NOTICES — Fenwing（Gecko for HarmonyOS）

本应用包含下列第三方组件。完整许可文本随应用提供于 `legal/LICENSE-MPL-2.0.txt`，
或从各项目主页获取。

| 组件 | 文件 | 许可证 |
|---|---|---|
| Gecko / GeckoView（含 libxul、libgeckoview、libgeckoxcomp） | libxul.so 等 | MPL-2.0 |
| SpiderMonkey（JS 引擎） | libmozjs-142a1.so | MPL-2.0 |
| gkcodecs（Gecko 内置编解码封装） | libgkcodecs.so | MPL-2.0 |
| FFmpeg（mozavcodec / mozavutil） | libmozavcodec.so、libmozavutil.so | LGPL-2.1-or-later |
| libvpx（经 lgpllibs 打包） | liblgpllibs.so | BSD-3-Clause |
| SQLite | libmozsqlite3.so | Public Domain |
| NSS（网络安全服务） | libnss3、libssl3、libsmime3、libnssutil3、libfreebl3、libsoftokn3 | MPL-2.0 |
| NSPR | libnspr4、libplc4、libplds4 | MPL-2.0 |
| zlib | libz.so | zlib License |
| OpenHarmony 系统库（输入法/时间服务） | libohinputmethod.so、libtime_service_ndk.so | Apache-2.0 / OpenHarmony 许可 |

说明：
- LGPL 组件（FFmpeg、libvpx）以动态库形式链接，未修改其源码；
- 如需对应源码，见 `SOURCE-OFFER.txt`；
- 本文件不构成法律意见；正式分发前建议法务复核。
