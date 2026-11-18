# Firefox / Gecko for HarmonyOS —— P2-2 浏览器壳完善（第一版）

> 时间：2026-11-18 · 目标：把"菜单/下载"从能用补到完整，向可日用推进

## 一、菜单补全

### 1) 链接：在新标签页打开（已真机验证）
- geckoview.js 在链接命中时增加「在新标签页打开链接」，通过已有 `airweb-tab-state` 通道
  发送 `{session:"__opentab__", title:"", url}`；
- ArkTS `onTitle` 放行该信封 → `BrowserPage.onGeckoTitleChanged` 识别 `__opentab__`
  → `openUrlInNewTab(url)`：新建 ArkTS 标签 + `createSession(engineIndex, url)`
  + `switchToSession` + 历史入栈 + 看门狗；
- 真机日志：
  ```
  menu shown id=1 rows=6
  resolveMenuCommand menu=1 item=1
  openUrlInNewTab https://example.com/ idx=1
  ```
  截图：`D:\ff-ohos\logs\shot_p22_newtab2.jpeg`（两个标签，新标签已加载链接）。

### 2) 图片：保存图片 / 复制图片地址（已实现）
- 「保存图片」在内容文档注入 `a[download]` 并点击，走 Gecko 下载管线 → 下载横幅/记录；
- 「复制图片地址」走 chrome 剪贴板。

### 3) 页面：复制页面地址 / 复制页面标题（已实现）
- "更多"子菜单中；复制走 clipboard，失败回退 `nsIClipboardHelper`。

## 二、下载管理（已实现）

- `DownloadsView` 新增：
  - 头部「清空」：删除记录 + 删除本地文件（`fileIo.unlinkSync`）；
  - 已完成记录「打开」：`fileUri.getUriFromPath` + `startAbility(viewData)` 交给系统打开。
- `BrowserDatabase` 新增 `deleteDownload(id)` / `clearDownloads(profileId)`。
- 真机验证：清空在空列表下无异常、面板刷新正常；「打开」路径已接入（待有记录时复测）。

## 三、待办 / 下一版

1. 「保存图片」在真实图片页复测（当前无图床页面，只有 demo 页）；
2. 下载完成通知与"下载中"列表实时刷新（目前依赖面板刷新/事件横幅）；
3. 历史/书签与引擎 URL 双向同步、地址栏自动补全；
4. 菜单定位在超大菜单下的进一步收敛（当前按内容区尺寸翻转）。

## 四、相关代码

- `gecko/src/main/resources/rawfile/omni.ja`（geckoview.js 菜单构造）
- `entry/src/main/ets/pages/BrowserPage.ets`（onTitle 信封、openUrlInNewTab、下载管理）
- `entry/src/main/ets/views/DownloadsView.ets`、`data/BrowserDatabase.ets`

---

## 五、历史/书签联动、地址栏补全与保存图片实测（2026-11-18 11:20 补充）

### 1) 历史联动（引擎侧驱动）
- 之前历史只在"用户主动导航"时写入；现在 pageLoad=stop 时由 ecordEngineHistory() 以**当前引擎 URL/标题**写历史（按 URL 去重，私密模式跳过），覆盖页内链接跳转、前进后退等场景。
- 导航写入同时更新 lastHistoryUrl，避免重复记录。

### 2) 地址栏补全
- AddressBar 增加 onInput 回调；BrowserPage.onAddressInput() 在书签 + 历史里做包含匹配，最多 8 条，显示为地址栏下方浮层，点击直接导航（pickSuggestion）。
- 待办：键盘输入焦点在部分场景会被系统窗口抢占（测试时点击地址栏后未获得焦点），需补 onFocus/请求焦点逻辑后再复测。

### 3) 保存图片（已实测）
- 右键/长按图片 → 「保存图片」→ Gecko 下载管线；**文件名修正**：data URI 按 mime 推导 image.svg/png/jpg，普通 URL 取 basename。
- 真机日志：
  `
  download event: 开始下载：image.svg
  download event: 下载完成：.../files/Downloads/image.svg
  `
- 「打开」增加按扩展名映射 mime（image/svg+xml、image/png、image/jpeg、text/plain、application/pdf）。
  注：mime 修正前曾用 text/plain 打开，系统落到文本编辑器；修正后待复测图片查看器。

### 4) 下载清空
- 已实测：清空按钮删除记录与本地文件，面板回到「暂无下载。」（空列表场景验证）。

## 六、待复测项
1. 修正 mime 后「打开」是否进入图片查看器；
2. 地址栏补全的焦点/键盘输入；
3. 历史面板中引擎驱动记录的展示。

---

## 七、收尾复测结果（2026-11-18 12:10）
- 地址栏补全：输入 exa → 下拉显示 https://example.com/（历史驱动），点击可导航。✅
- 历史联动：历史面板显示引擎记录的 https://example.com/。✅
- 保存图片：下载完成：.../Downloads/image.svg（文件名/扩展名正确）。✅
- 下载清空：删记录+删文件，回到「暂无下载」。✅
- 「打开」：mime 已按扩展名映射；图片查看器落地仍待系统支持验证（本机 SVG 无默认查看器）。
