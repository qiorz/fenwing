# SOURCE OFFER — 对应源码获取说明（MPL-2.0 / LGPL 合规）

本应用（AirWeb）包含 MPL-2.0 与 LGPL-2.1+ 组件。按许可证要求，提供对应源码获取方式：

## 1. Gecko 引擎（MPL-2.0）

- 上游：mozilla-central，修订 `5836a062726f715fda621338a17b51aff30d0a8c`（Gecko 142.0a1）；
- 本地修改：OHOS 移植层（`widget/openharmony/`、`ports/ohos/`、`browser/base/content/geckoview*`、
  omni 资源中的 geckoview.js 等），见构建工作区 `D:\ff-ohos` 与 WSL `/home/dev/ff/gecko`；
- 构建方式：`D:\ff-ohos\scripts\build-gecko-full.sh`、`build-omni.sh`、`stage-engine.sh`；
- 获取：随分发提供本仓库/工作区副本，或按上述脚本从上游重建。

## 2. FFmpeg / libvpx（LGPL-2.1+ / BSD）

- 以动态库形式链接（libmozavcodec.so、libmozavutil.so、liblgpllibs.so），未修改源码；
- 上游源码：https://ffmpeg.org / https://chromium.googlesource.com/webm/libvpx；
- 重建脚本：Gecko 构建系统内 `media/ffvpx`、`media/libvpx`（`mach build`）。

## 3. 其他 MPL-2.0 组件

NSS、NSPR、SpiderMonkey、gkcodecs 均随 mozilla-central 源码提供。

## 4. 如何取得

如需对应源码副本，请通过分发渠道提供的联系方式索取，或直接使用上述上游修订 +
`D:\ff-ohos` 工作区中的构建脚本重建（构建说明见 `docs\Firefox移植-P3工程化.md`）。
