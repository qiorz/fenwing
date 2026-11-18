# Firefox / Gecko for HarmonyOS —— P1.5 菜单与界面压缩

> 完成时间：2026-11-18

## 一、界面压缩（已真机验证）

目标：把顶栏/底栏占用的行数压到最少，把空间还给内容。

改动：
1. **地址栏单行紧凑化**
   - 按钮 36→30 vp、padding 0、间距缩小；
   - 输入框高度 36→30；
   - 去掉行内的"私密"徽章（私密状态移到工具条）；
   - "前往"按钮 52→64 vp（避免文字被省略成"…"）。
2. **底栏由三行压缩为两行**
   - 删除独立的"查找/缩放"整行（查找与缩放并入工具条）；
   - 工具条单行：`书签 历史 下载 设置 收藏 私密 … 查找 − 100% +`（高度 26 vp）；
   - 标签栏行：chip 宽度 150 vp、高度 32 vp，`+` 新建、`☰` 打开设置面板。
3. 全屏模式（DOM fullscreen）下自动隐藏地址栏与标签栏，页面占满窗口。

效果：内容区高度增加约 80–100 vp（原来三行底栏 + 较高地址栏）。

## 二、原生菜单浮层（P1.5）

实现链路：
```
Gecko XUL 菜单 (nsXULPopupManager::ShowMenu/ShowPopup)
  → OHOSMenuBridge_Show 序列化 JSON {menuId, anchor{x,y,w,h}, items[{kind,id,label,accel,checked,disabled,hidden,items}]}
  → libgeckoview tsfn → registerMenuCallback
  → EntryAbility onMenu → AppStorage('geckoMenu' + 自增 seq)
  → BrowserPage 解析并渲染菜单浮层
  → 点项: resolveMenuCommand(menuId,itemId,0)
  → 点外部: closeNativeMenu(menuId)
```

UI 支持：分隔线、勾选态（✓）、禁用态（灰显）、快捷键文本（accel）、子菜单缩进（depth ≤ 2）、按锚点定位（`anchor.x/y+h`），空白处点击关闭。

真机验证（合成菜单负载 `--ps menutest 1`）：
```
BrowserPage: menu shown id=9001 rows=5
GeckoViewBoot: resolveMenuCommand menu=9001 item=1
```
截图见 `D:\ff-ohos\logs\shot_menu_view.jpeg`（菜单渲染）与 `shot_mt5.jpeg`。

## 三、真实菜单触发：现状与结论

尝试了两条真实触发路径：
1. **长按页面**（`uitest longClick`）：无菜单、无回调；
2. **右键**（通过 `GeckoViewBoot.mouseDown/up(button=2)` 在内容中心派发）：无菜单、无回调；
3. **`<select>` 下拉**：页面 select 正常显示，但下拉未走 XUL popup 桥（classic geckoview.xhtml 轨道下由内容/原生控件处理）。

结论：当前 **classic（geckoview.xhtml）轨道下，内容区 context menu 没有进入 `OHOSMenuBridge_ShowContextMenu`**（port 的门控/形态判断或 classic 轨道不挂接），因此菜单桥在当前 UI 轨道上是"通路已就绪、事件未接上"。

要让真实右键/长按菜单生效，需要下一轮做其中之一：
- 排查 `OHOSMenuBridge_ShowContextMenu` 的形态门控（是否只对 2in1 放行；本机 devicetype=tablet）；
- 或将 uiMode 切到 `native`（browser.xhtml）轨道——但那是整套 chrome UI 的迁移，工作量大；
- 或在 classic 轨道给内容区补一个"长按 → 构造右键事件"的宿主入口（Gecko 侧仍走 nsContextMenu），需要确认 Gecko 的 contextmenu 触发条件（mousedown with button=2 + proper modifiers）。

## 四、调试入口（新增）

```
--ps menutest 1   注入示例菜单负载，验证菜单浮层 UI
--ps ctxmenu 1    启动后 4s 在内容中心派发右键，验证真实 context menu 通路
```

## 五、已知限制

1. 菜单浮层位置按 anchor 直接定位，未做边界翻转（贴边时可能超出窗口）；
2. 子菜单以缩进平铺展示（port 暂不支持 flyout 悬停展开，见其注释）；
3. 真实菜单事件未接通（见 §三）；
4. 合成菜单点击会向 Gecko 发送无效 menuId，仅用于 UI 验证。
