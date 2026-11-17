Firefox for HarmonyOS — Gecko 引擎二进制包 v1.0.0
=================================================

内容
----
  gecko/libs/arm64-v8a/*.so                    HSP 运行时要装载的全部原生库
                                               （libxul.so 含 .permission 段，JIT 版）
  gecko/src/main/libs/arm64-v8a/libmozjs.so     gecko_napi (CMake) 链接用
  gecko/src/main/libs/arm64-v8a/include/       SpiderMonkey 公开头文件
  gecko/src/main/resources/rawfile/omni.ja     GRE 资源包（不是普通 zip，请勿解压）

  install.ps1 / install.sh                     一键铺到 app/ 对应位置

来源
----
  Gecko 142.0a1 (mozilla-central 5836a062726f715fda621338a17b51aff30d0a8c)
  + OHOS 移植层（见仓库 engine/patches/firefox-ohos-gecko-5836a06272.patch）
  设备验证：HUAWEI MatePad Edge QXS-W00 / HarmonyOS 7.0.0.111 / API 26 / arm64-v8a

用法
----
  Windows:
    powershell -ExecutionPolicy Bypass -File .\install.ps1 -AppPath D:\path\to\firefox-ohos\app

  Linux / WSL / macOS:
    ./install.sh /path/to/firefox-ohos/app

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
  二进制来自 MPL-2.0 的 Gecko 代码。对应源码获取方式见仓库根目录 NOTICE 与
  engine/PROVENANCE.md。Gecko / Firefox 是 Mozilla Foundation 的商标，本包
  与 Mozilla 无隶属关系。
