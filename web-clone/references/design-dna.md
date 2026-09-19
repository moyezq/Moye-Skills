# Design DNA

视觉复刻 / 内容爆改用。忠实复刻不用：真源码就是真相。

把「那个站的感觉」做成可版本化 JSON，让第 6 步「DNA 留着、内容换掉」有据。完整骨架由 `dna-scaffold.mjs` 生成，不要手抄 schema。

## 三层

1. `design_system` — 可测量 token（色 / 字 / 间距 / 布局 / 形状 / 阴影 / 图标 / 动效 / 组件）→ 落 CSS 变量
2. `design_style` — 主观感知（mood / 视觉语言 / 构图 / 图像 / 交互手感 / UI 语气）
3. `visual_effects` — 超出普通 CSS 的渲染；`effect_intensity` 选 lightweight CSS / medium Canvas+GSAP / heavy Three.js

## 工作流

1. Structure：看脚手架字段，裁掉无关维。
2. Analyze：从 recon 抽色（`cssVariables` + section 背景）、字体、间距（截图 + `sections[].rect`）、特效信号（three/gsap/lenis/canvas）。三档截图判 mood。填不出标 `TODO`。
3. Generate：token → CSS；按 style 做取舍；按 intensity 选实现。素材用 `asset-harvest.mjs` 取原站真图。

`visual_effects` 标了 heavy / WebGL / shader 的特效本身走 `reverse-engineering.md` + `effect-extraction.md`，DNA 只管特效之外的设计层。
