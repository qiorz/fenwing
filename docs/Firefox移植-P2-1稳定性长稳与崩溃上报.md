# Firefox / Gecko for HarmonyOS —— P2-1 稳定性长稳与崩溃上报

> 时间：2026-11-18 · 设备：MatePad Edge QXS-W00（HarmonyOS 7.0.0.111 / API 26）
> 目标：从"能跑"走向"可日用"——验证多轮启停/多标签/导航下的稳定性与内存趋势，并建立可用的崩溃现场记录。

## 一、长稳压测（已执行）

工具：`D:\ff-ohos\scripts\soak-test.ps1`
每轮动作：
1. `aa force-stop` → 冷启动（每 3 轮一次走**会话恢复**，其余 `--ps noresume` 干净启动）；
2. 等待首帧 → 点 `+` 新建 2 个标签 → 切换标签；
3. 地址栏输入并回车导航（`https://example.com/x`）；
4. 记录 RSS（`ps -p <pid> -o pid,rss`）与 `MemAvailable`，检测进程是否消失；
5. 进程消失时自动抓取 `hilog FATAL/SIGSEGV/SIGILL/SIGABRT` 尾部到 `crashes.log`。

### 结果

| 轮次 | 场景 | 崩溃 | RSS（tabs/switch/nav，KB） |
|---|---|---|---|
| 6 轮 | 启停 + 建标签 + 切换 | 0 | 303,620 – 330,468 |
| 8 轮 | 上述 + 地址栏导航 | 0 | 301,836 – 308,664 |

结论：
- 两种循环均 **0 崩溃**，进程无异常退出；
- 多轮循环后 RSS **无单调增长**（切换/导航后稳定在 ~303 MB），暂未发现明显泄漏；
- 冷启动瞬间 RSS 在 309–370 MB 波动（页面加载/合成器预热），稳定后回落，属于预期范围；
- 每次 `force-stop` 都被判为异常退出，下次启动恢复会话（见下）。

## 二、崩溃现场记录（已实现）

1. **异常退出判定**：`engine.run` 运行标记（正常退出清除）→ 启动时判定；
2. **恢复横幅携带现场**：
   ```
   BrowserPage: unclean exit detected, restored 2 tabs, last=https://example.com/x
   ```
   横幅文案为「检测到上次异常退出，已自动恢复 N 个标签（上次停留：<URL>）」；
3. **宿主侧崩溃取证**：压测脚本发现 pid 消失时，自动保存崩溃时间点附近的
   `hilog` FATAL/信号日志到 `D:\ff-ohos\logs\soak\crashes.log`；
4. **会话恢复**：`session.json`（400ms 防抖、tmp+rename）+ 引擎会话重建，已在此前 P0 验证。

## 三、限制与后续

| 项 | 现状 | 后续建议 |
|---|---|---|
| minidump | 构建时 `--disable-crashreporter`，无 Breakpad | 需要重编引擎启用 crashreporter（成本高）或接入系统 faultloggerd（需系统权限） |
| faultlog 读取 | `/data/log/faultlog` 对 shell 拒绝访问 | 需 root/ACL 或系统接口；当前以 hilog 取证替代 |
| 崩溃栈质量 | port 的 GeckoSignalHandler 会打印 PC/回溯到 hilog | 可在应用下次启动时提示"查看日志"，或把关键片段写入沙箱文件 |
| 长稳覆盖 | 已覆盖启停/建标签/切换/导航 | 建议增加到 30+ 轮、加入关闭标签、下载、文件选择、全屏、页面内滚动/缩放 |
| 内存回收 | 关闭标签后 RSS 回落未单独量化 | 增加"关闭标签后 RSS"采样与阈值告警 |

## 四、复现方式

```powershell
# 8 轮（含导航），结果写入 D:\ff-ohos\logs\soak\soak.csv
powershell -NoProfile -ExecutionPolicy Bypass -File D:\ff-ohos\scripts\soak-test.ps1 -Cycles 8
```

崩溃记录：`D:\ff-ohos\logs\soak\crashes.log`；采样数据：`D:\ff-ohos\logs\soak\soak.csv`。

---

## 五、扩面压测（2026-11-18 11:00 补充）

脚本已扩展：新增"关闭第二个标签"步骤与 RSS 阈值告警（450 MB），并继续覆盖建标签/切换/导航。

结果（8 轮，真机）：
`
cycle 1: launch=368428KB tabs=316828KB switch=300208KB nav=303372KB close=303400KB crashed=False
...
cycle 8: launch=359900KB tabs=303884KB switch=300056KB nav=305636KB close=305636KB crashed=False
SUMMARY cycles=8 rss_min=300056KB rss_max=303856KB rss_avg=302050KB crashes=0
`
- 关闭标签后 RSS 与导航后基本持平（~304–306 MB），未观察到回落异常或增长；
- 全程 0 崩溃、无阈值告警；
- 结论：启停/多标签/切换/导航/关闭 组合下内存与稳定性表现稳定。

## 六、收尾压测（15 轮，2026-11-18 11:30）

`
cycle 1 : launch=376632KB tabs=314744KB switch=317520KB nav=316512KB close=316608KB
...
cycle 15: launch=312112KB tabs=312788KB switch=301756KB nav=298264KB close=298380KB
SUMMARY cycles=15 rss_min=298084KB rss_max=317520KB rss_avg=302459KB crashes=0
`
- 15 轮混合（冷启/恢复、建 2 标签、切换、导航、关闭标签）**0 崩溃**；
- RSS 全程 298–317 MB，无单调增长，无阈值告警（阈值 450 MB）；
- P2-1 计划范围内（长稳 + 崩溃现场记录）**已完成**；minidump/faultloggerd 作为后续增强项。
