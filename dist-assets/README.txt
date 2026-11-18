Fenwing — Gecko 引擎二进制包 v1.2.0
==================================

内容
----
  gecko/libs/arm64-v8a/*.so                    HSP 运行时要装载的全部原生库
                                               （llvm-strip 全量瘦身；libxul.so 含
                                                .permission 段，JIT 版）
  gecko/src/main/libs/arm64-v8a/libmozjs.so     gecko_napi (CMake) 链接用
  gecko/src/main/libs/arm64-v8a/include/       SpiderMonkey 公开头文件
  gecko/src/main/resources/rawfile/omni.ja     GRE 资源包，deflate 压缩版（约 20 MB；
                                               不是普通 zip，请勿解压）

  install.ps1 / install.sh                     一键铺到 app/ 对应位置

体积（相对 v1.0.0）
-------------------
  gecko libs        302 MB（未 strip）→ 213 MB
  omni.ja           65.5 MB（STORED）  → 20.4 MB（deflate -6）
  HSP 安装包         292.3 MB           → 250.2 MB（-14.4%）
  首帧冷启动         5890 ms            → 5858 ms（无退化）

来源
----
  Gecko 142.0a1 (mozilla-central 5836a062726f715fda621338a17b51aff30d0a8c)
  + OHOS 移植层（见仓库 engine/patches/firefox-ohos-gecko-5836a06272.patch）
  设备验证：HUAWEI MatePad Edge QXS-W00 / HarmonyOS 7.0.0.111 / API 26 / arm64-v8a

用法
----
  Windows:
    powershell -ExecutionPolicy Bypass -File .\install.ps1 -AppPath D:\path\to\airweb\app

  Linux / WSL / macOS:
    ./install.sh /path/to/airweb/app

然后用 DevEco Studio 打开 app/，配置本机签名后构建 HAP + HSP。

关于 JIT
--------
  本包的 libxul.so 是启用 JIT 的版本，ELF 中带 .permission 段，声明需要：
    ohos.permission.kernel.ALLOW_WRITABLE_CODE_MEMORY
    ohos.permission.kernel.DISABLE_CODE_MEMORY_PROTECTION

  这两条是 ACL 权限，只有带 ACL 的签名 profile 才会生效（需要 AGC 申请）。
  用普通的自动签名证书时：应用仍可安装运行，但引擎会自行降级为解释器模式
  （JS 计算密集场景慢 14–38 倍，见仓库 docs/ 中的性能基线）。

许可
----
  Fenwing 使用 Mozilla Public License 2.0。二进制来自 MPL-2.0 的 Gecko 代码，
  对应源码的获取方式见仓库 SOURCE-OFFER.md 与 engine/PROVENANCE.md。
  FFmpeg / libvpx 以动态库形式链接（LGPL-2.1+ / BSD），未修改源码。
  "Firefox"、"Gecko" 是 Mozilla Foundation 的商标；本项目与 Mozilla 无隶属关系，
  仅作事实性技术说明，不发布任何 Mozilla 品牌产物。
