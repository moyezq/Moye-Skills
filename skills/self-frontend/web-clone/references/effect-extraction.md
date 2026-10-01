# 特效证据纪律

配合 `reverse-engineering.md`。三件套：分级 → no-compensation → baseline-first。

## 分级

TEARDOWN 里每条渲染事实打标签；未标 = `GUESS`。`GUESS` 级实现照抄前必须升到 `SOURCE`。

| 标签 | 含义 |
|------|------|
| `SOURCE` | 真源码行、source-map 模块、运行时 dump、抓到的 shader、帧捕获、带 hash 的响应体 |
| `PARTIAL` | 名字/切片/缺 uniform 的 shader，还不够定论 |
| `GUESS` | 视觉拟合、命名推断、手调魔数 |

## no-compensation

不要靠改亮度 / 速度 / 位置 / 噪声去掩盖时序、坐标、FBO、状态错误。拟合常数仍是 `GUESS`，写明要什么证据才能升级。画面像了 ≠ 接线对了。

## baseline-first

先 RAW REPLAY（真实 draw call / shader / uniform，不优化不换框架）→ 逐帧比对过闸 → 才允许重构工程化。

收尾标：`DONE_BASELINE_VERIFIED` / `DONE_PROJECTIZED` / `DONE_BASELINE_WITH_GAPS`。复现物放 `$R\RECON\baseline\`。

## 无源码时

在 WebGL/WebGPU 拦截 draw call、program、shader 源、uniform、FBO。抓到的算 `SOURCE`，再走闸门。已装 `web-shader-extractor` 时，无源重特效可把捕获段委托给它，产物并回 `$R` 后继续本 skill 第 5–6 步。
