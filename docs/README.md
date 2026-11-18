# 文档索引

这些文档是移植过程的原始记录，按阶段排列。数字、日志、限制条件都来自真机验证
（HUAWEI MatePad Edge QXS-W00 / HarmonyOS 7.0.0.111 / API 26 / arm64-v8a）。

> 2026-11-18：项目更名为 **AirWeb**（原名 "Firefox for HarmonyOS"），文档标题保留历史名称，
> 正文中的产品名以 AirWeb 为准。

| 文档 | 内容 | 阶段 |
|---|---|---|
| [环境体检报告](Firefox-HarmonyOS-API26-移植环境体检报告.md) | 工具链、SDK、上游与社区现状逐项核查，缺口与风险 | 启动 |
| [资料包分析与下一步计划](Firefox移植-资料包分析与下一步计划.md) | 旧工程（M0 骨架）与本工程的资产对账、合并选项 | 启动 |
| [项目审视与下一步计划](Firefox移植-项目审视与下一步计划.md) | 第一轮：已打通能力、架构约束、技术债 | 中期 |
| [P0 稳定性说明](Firefox移植-P0稳定性说明.md) | 崩溃检测、会话恢复、20 s 看门狗、错误覆盖层 | P0 |
| [P1 可用性说明](Firefox移植-P1可用性说明.md) | 下载、文件选择、全屏、页内查找、缩放 | P1 |
| [P1.5 菜单与界面压缩](Firefox移植-P1.5菜单与界面压缩.md) | 三行底栏压两行、原生菜单浮层、真实菜单触发结论 | P1.5 |
| [P2-1 稳定性长稳与崩溃上报](Firefox移植-P2-1稳定性长稳与崩溃上报.md) | 15 轮压测 0 崩溃、RSS 采样、崩溃现场记录 | P2-1 |
| [P2-2 浏览器壳完善](Firefox移植-P2-2浏览器壳完善.md) | 新标签打开、保存图片、下载管理、历史/补全 | P2-2 |
| [P2-3 体积与性能](Firefox移植-P2-3体积与性能.md) | HSP 292→250 MB、omni deflate、≤200 MB 尝试与回退 | P2-3 |
| [P3 工程化](Firefox移植-P3工程化.md) | 一键脚本、快照校验、冒烟/长稳、本地 CI | P3 |
| [P4 合规与分发](Firefox移植-P4合规与分发.md) | 品牌更名、MPL/LGPL、权限隐私、分发与签名清单 | P4 |
| [项目审视（第二轮）](Firefox移植-项目审视（第二轮）.md) | 2026-11-18 的能力总览、硬约束、风险与下一阶段路线 | 复盘 |
| [性能基线报告](Firefox移植-性能基线报告.md) | JIT vs 解释器的真机数据、测试方法、ACL 前提 | 专项 |

## 合规材料

- [SOURCE-OFFER.md](SOURCE-OFFER.md) —— MPL/LGPL 对应源码获取说明
- [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) —— 第三方组件与许可证清单
- [LICENSE-MPL-2.0.txt](LICENSE-MPL-2.0.txt) —— MPL 2.0 全文
- 应用内随包副本：`app/entry/src/main/resources/rawfile/legal/`

## 阅读顺序建议

1. 先看仓库根 [README](../README.md) 的「架构」「体积」「三个坑」；
2. 复现构建 → 环境体检报告 + [engine/README.md](../engine/README.md)；
3. 改功能 → 对应 P 阶段文档的「相关代码」小节；
4. 发布前 → P4 的检查清单 + 本目录合规材料。

## 工程规范（另一套）

`app/spec/gecko-porting-program/` 下是与代码同仓维护的立项与治理文档：
决策包、实施记录、M1 报告、风险登记、安全合规、上游维护策略、任务清单。
它们比 `docs/` 更偏「项目管理」，`docs/` 更偏「技术复盘」。
