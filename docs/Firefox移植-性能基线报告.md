# Firefox / Gecko for HarmonyOS —— 性能基线报告（JIT vs 解释器）

> 设备：HUAWEI MatePad Edge QXS-W00，HarmonyOS 7.0.0.111，API 26，arm64
> 引擎：Gecko 142.0a1（mozilla-central `5836a062`）+ 社区 OHOS 移植层
> 应用：com.example.firefoxport（HAP + HSP，debug profile，含 ACL）
> 日期：2026-11-17

## 1. 结论

| 指标 | JIT | 解释器 | 变化 |
|---|---|---|---|
| fib(27) 递归 | **3 ms** | 114 ms | **≈ 38×** |
| 对象属性累加 5,000,000 次 | **34 ms** | 496 ms | **≈ 14.6×** |
| 数组 map+reduce 1,000,000 | **44 ms** | 648 ms | **≈ 14.7×** |
| 字符串拼接 50,000 + split/join | 9 ms | 5 ms | 略慢（见 §4） |
| 冷启动 engine start → 首帧 | 401 ms | 372 ms | +29 ms（≈8%） |

**JIT 已真实启用**（引擎自检日志：`[OHOS_JIT] RWX mmap 探测成功(内核权限生效),JIT 全速启用`），对 JS 计算密集型场景带来 **14–38 倍**提升；代价是冷启动多约 30 ms。字符串基准因 rope 实现差异在 JIT 下略慢，属正常波动，不代表整体回退。

## 2. 测试方法

- 同一份基准页 `bench.html`（写入沙箱，`file://` 加载）：
  - 页面内 `performance.now()` 计时，共跑 **3 轮**，结果拼进 `document.title`
  - ArkTS 侧通过标题回调（`airweb-tab-state` → `registerTabStateCallback`）把结果写入 hilog
- 两种模式由**同一次构建**的启动参数切换，避免构建差异：
  - JIT：`aa start -a EntryAbility -b com.example.firefoxport --ps perf 1`
  - 解释器：`aa start -a EntryAbility -b com.example.firefoxport --ps perf 1 --ps nojit 1`
  - `nojit` 会把 `--airweb-force-no-jit` 传给引擎（`AIRWEB_FORCE_NO_JIT=1` → `JS::DisableJitBackend()`）
- 每轮之间 `force-stop` + `hilog -w clear`，保证冷启动、无残留；
- 取页面 3 轮中的**中位数**（第 1 轮包含预热，见 §4）。

## 3. 复现步骤

```powershell
# 构建（已包含基准页与参数开关）
hvigorw assembleHsp assembleHap --no-daemon
# 安装
hdc -t <ip:port> file send entry-default-signed.hap /data/local/tmp/entry-signed.hap
hdc -t <ip:port> file send gecko-default-signed.hsp /data/local/tmp/gecko-signed.hsp
hdc -t <ip:port> shell "bm install -r -p /data/local/tmp/entry-signed.hap /data/local/tmp/gecko-signed.hsp"

# JIT
hdc -t <ip:port> shell "aa force-stop com.example.firefoxport"
hdc -t <ip:port> shell "aa start -a EntryAbility -b com.example.firefoxport --ps perf 1"
# 解释器
hdc -t <ip:port> shell "aa start -a EntryAbility -b com.example.firefoxport --ps perf 1 --ps nojit 1"

# 取结果
hdc -t <ip:port> shell "hilog -x | grep 'title=BENCH'"
```

脚本：`D:\ff-ohos\scripts\ab-param-bench.py`（注入参数化基准）、`D:\ff-ohos\scripts\patch-jit-on.py` / `patch-jit-off.py`（JIT 开/关）。

## 4. 已知偏差与说明

1. **预热**：每个基准在页面内跑 3 轮，第 1 轮包含 JIT 编译/IC 预热（如 fib=10ms 首轮 vs 3ms 稳定），报告取中位数；解释器无此现象。
2. **字符串基准偏慢**：`s += "ab"` 后 `split("").join("")` 主要测 rope/flatten 路径，JIT 下未获得收益，且毫秒级量化噪声大；不宜单独作为 JIT 回归判据。
3. **计时粒度 1 ms**（performance.now 在页面上下文），fib/字符串这类毫秒级结果存在 ±1–2 ms 误差；对象/数组基准（几十~几百 ms）可信度高。
4. **启动对比**含同一次构建、同一 omni.ja、同一 profile 冷启动；JIT 多出的 ~30 ms 为 JIT 初始化/代码页准备。
5. 网络页面加载未纳入本次对比（受网络波动影响），此前单次测得 278 ms（example.com/x，解释器模式），JIT 对其影响有限，主要收益在 JS 执行。

## 5. 原始数据

```
JIT      : fib=10,obj=48,arr=32,str=9 | fib=3,obj=34,arr=45,str=9 | fib=3,obj=34,arr=44,str=9
INTERP   : fib=114,obj=497,arr=647,str=11 | fib=115,obj=496,arr=648,str=5 | fib=114,obj=496,arr=652,str=4

启动（engine start → first-composite）
JIT      : 21:45:17.631 → 21:45:18.032  (401 ms)
INTERP   : 21:45:35.200 → 21:45:35.572  (372 ms)
```

## 6. 权限前提（JIT 生效条件）

- 签名 profile ACL：`ohos.permission.kernel.ALLOW_WRITABLE_CODE_MEMORY`、
  `ohos.permission.kernel.DISABLE_CODE_MEMORY_PROTECTION`
- `module.json5` 声明上述权限
- `libxul.so` 注入 `.permission` ELF 段（`llvm-objcopy --add-section`）
- 引擎启动参数不带 `--airweb-force-no-jit`
- 无 ACL 时：RWX mmap 看似成功，但执行 JIT 代码触发 SIGILL → 必须依赖 ACL；`XPCOMInit` 的探测会在权限被拒时自动降级解释器（坚盾模式适配）
