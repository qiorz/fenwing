# Firefox / Gecko for HarmonyOS —— P4 合规与分发（v1）

> 时间：2026-11-18 · 目标：让这个移植可以合法、清晰地交付给他人（侧载/内测/企业分发），并为将来上架做准备

## 一、品牌与命名

| 项 | 处理 |
|---|---|
| 应用显示名 | `firefoxport` → **AirWeb**（可在 `AppScope/resources/base/element/string.json` 一行修改） |
| 界面文案 | 移除 "Firefox 基线" 字样，改为"Gecko 内核基线"（事实描述） |
| 商标 | 不使用 Firefox 名称、Logo、图标；不暗示 Mozilla 官方背书 |
| 包名 | 暂保留 `com.example.firefoxport`（不影响合规，正式发布前建议改为自有域名反写） |

## 二、开源许可（MPL-2.0 / LGPL）

随应用提供（`entry/.../rawfile/legal/`）：

- `LICENSE-MPL-2.0.txt` —— MPL 2.0 完整文本；
- `THIRD-PARTY-NOTICES.txt` —— 第三方组件与许可证清单；
- `SOURCE-OFFER.txt` —— 对应源码获取方式（Gecko 上游修订 + 本地移植修改 + 构建脚本）。

MPL 义务要点：
1. 修改过的 MPL 文件需以 MPL 分发（我们修改的 Gecko 文件头保留 MPL 声明）；
2. 以可执行形式分发时，须告知接收者如何取得源码（本项目的 SOURCE-OFFER）；
3. 不得移除版权/许可声明。

LGPL（FFmpeg、libvpx）：动态库形式链接、未修改源码；提供源码获取方式即可。

## 三、第三方组件

见 `THIRD-PARTY-NOTICES.md`（NSS/NSPR/SpiderMonkey/gkcodecs/SQLite/zlib/FFmpeg/libvpx/OH 系统库）。
建议正式发布前由法务复核一遍清单与链接方式。

## 四、权限与隐私

| 项 | 说明 |
|---|---|
| ACL：`ALLOW_WRITABLE_CODE_MEMORY` | JIT 引擎需要可写可执行内存（JS 性能 14–38×），不涉及系统修改 |
| ACL：`DISABLE_CODE_MEMORY_PROTECTION` | 同上，配合 JIT 使用 |
| `ohos.permission.INTERNET` | 浏览网页 |
| 文件访问 | 仅应用沙箱（下载目录、缓存）；文件选择经系统 Picker 授权 |
| 数据 | 历史/书签/下载/会话仅存本机；**无遥测、无自动崩溃上传** |
| 日志 | 仅本地调试日志，不含用户内容上传 |

隐私说明建议随发布提供（`PRIVACY.md`，v1 阶段以本文档 + 应用内"关于"承载）。

## 五、分发与签名

1. **调试签名**（当前）：DevEco 自动签名 + ACL 证书，仅限本机/内测侧载；
2. **发布签名**：用自有证书重新签名 HAP/HSP（`sign-firefoxport.ps1` 可参考），
   并在 AGC/发布平台登记证书指纹；
3. **安装步骤**（随包 README）：
   - 设备需 HarmonyOS API 26+、arm64；
   - `hdc install` 或 `bm install -p entry-signed.hap gecko-signed.hsp`（两者需同装）；
   - 首次启动会解压 omni 资源，冷启动约 6s；
4. **版本策略**：`versionCode` 单调递增；`versionName` 语义化（当前 1.0.0 → 下一版 1.0.1/1.1.0）；
5. **渠道**：侧载 HAP/HSP（当前）、企业分发，或应用市场（需另备隐私政策、权限说明、软著等材料）。

## 六、发布检查清单

- [x] 应用名/界面去除 Firefox 商标
- [x] MPL 文本、第三方清单、源码提供说明随包
- [x] ACL/权限用途说明
- [x] 隐私说明（无遥测/本地上传）
- [ ] 正式发布证书与 Profile
- [ ] 包名改为自有反写域名
- [ ] 法务复核第三方许可
- [ ] （可选）应用市场材料

## 七、当前产物

- `docs/`：`LICENSE-MPL-2.0.txt`、`THIRD-PARTY-NOTICES.md`、`SOURCE-OFFER.md`、本文档；
- 应用内：`entry/src/main/resources/rawfile/legal/`（随包分发）；
- `verify-snapshot.ps1` 已增加许可文件与品牌检查，CI 会在缺失时失败。

---

## 八、v1 已验证（2026-11-18 13:15）

- 真机窗口标题/应用名显示 **AirWeb**（EntryAbility_label 与 pp_name 均改为 AirWeb）；
- erify-snapshot.ps1 新增项全 PASS：
  - legal 三件套随包（LICENSE/THIRD-PARTY/SOURCE-OFFER）
  - app_name 与 Index.ets 无 Firefox 品牌
- 本地 CI：build → verify → smoke 全 PASS（含许可/品牌检查）。

## 九、v2 待办（发布前）

1. 正式发布证书/Profile（替换 DevEco 调试签名）；
2. 包名改为自有反写域名（如 com.<company>.airweb，需同步 ACL 申请与签名）；
3. 法务复核第三方许可（重点 FFmpeg LGPL 动态链接声明）；
4. 可选：应用市场材料（隐私政策、权限场景说明、软著）。
