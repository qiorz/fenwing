# Firefox / Gecko for HarmonyOS —— P0 稳定性实现说明

> 目标：单进程架构下（无 e10s、无崩溃隔离），让"崩溃/被杀/加载失败"不再表现为白屏或无声退出。
> 完成时间：2026-11-17

## 一、实现的三件事

### 1) 非正常退出检测 + 会话恢复

- `SessionStore`（`entry/src/main/ets/service/SessionStore.ets`）：
  - `session.json`：每次标签变化后 400ms 防抖落盘（先写 `.tmp` 再 rename，避免半截文件）；
  - `engine.run`：引擎启动前写入的"运行中"标记；正常退出（`UIAbility.onDestroy`）删除。
- 启动时：若 `engine.run` 存在 → 上次进程未正常结束（崩溃 / OOM / force-stop）。
- `BrowserPage.bootstrap()` 读取会话并恢复：
  - 每个保存的标签重建 ArkTS TabModel；
  - 第一个标签复用引擎 browser 0，其余按序 `createSession(i, url)`；
  - 恢复激活标签（`switchToSession`），并 `loadUrlForSession` / `forceRepaint`；
  - 恢复成功且检测到异常退出时，顶部显示横幅：
    **"检测到上次异常退出，已自动恢复 N 个标签"**（可点"知道了"关闭）。

### 2) 页面加载失败/超时错误页

- 20 秒看门狗：进入加载（导航、启动页、重试）即武装；收到 `pageLoad=stop` 则解除；
- 触发后显示覆盖层：
  - 标题「页面加载失败」
  - 说明「页面加载超时：请检查网络连接，或重试。」
  - 按钮「重试」（`reloadForSession` 并重新武装看门狗）、「回到首页」。
- 覆盖层是 ArkTS UI，位于 XComponent 之上，不依赖 Gecko 是否能渲染错误页。

### 3) 测试/诊断入口（不影响正常用户）

`aa start` 参数（仅调试用）：
- `--ps perf 1`：加载内置基准页（性能测试）
- `--ps nojit 1`：强制解释器模式（A/B 对比）
- `--ps url <url>`：覆盖启动页（错误页/长稳测试）
- `--ps noresume 1`：跳过会话恢复（复现首次启动）

## 二、真机验证结果

| 场景 | 操作 | 结果 |
|---|---|---|
| 崩溃恢复 | 开 2 个标签 → `aa force-stop` → 重启 | hilog：`unclean exit detected, restored 2 tabs`；界面顶部横幅 + 2 个标签恢复 + 内容正常 |
| 会话持久化 | 同上，重启后 active tab / URL 正确 | ✅ |
| 加载超时错误页 | `--ps url http://10.255.255.1/ --ps noresume 1`，等 20s | hilog：`load watchdog fired`；界面出现「页面加载失败 + 重试/回到首页」覆盖层 |

截图：`D:\ff-ohos\logs\shot_p0_recovered.jpeg`、`D:\ff-ohos\logs\shot_p0_err3.jpeg`

## 三、已知边界

1. **force-stop / 系统杀进程都被视为"异常退出"**：下次启动会显示恢复横幅（这是有意的保守策略）；
2. 正常退出才清 marker：目前只有 `onDestroy` 被系统调用时才算"干净退出"，用户强制杀进程仍提示恢复；
3. 看门狗只覆盖"卡住没响应"，若 Gecko 自身返回错误页则不走该覆盖层（端口当前错误页表现取决于 Gecko 内建 neterror）；
4. 无 minidump/崩溃栈自动上报：需要在 `libgeckoview.so` 的 `GeckoSignalHandler` 或系统 faultlogger 上做进一步接入（P0 后续项）；
5. 会话恢复不保留每标签的滚动位置/表单内容/历史栈（历史栈是 ArkTS URL 栈，恢复后从 URL 重新加载）。

## 四、代码位置

- `entry/src/main/ets/service/SessionStore.ets`（新增）
- `entry/src/main/ets/entryability/EntryAbility.ets`（标记、参数、`url` 覆盖）
- `entry/src/main/ets/pages/BrowserPage.ets`（恢复、横幅、看门狗、错误覆盖层、会话落盘）
- 脚本：`D:\ff-ohos\scripts\p0-entry.py`、`p0-browserpage.py`、`p0-watchdog2.py`、`p0-skipresume.py`
