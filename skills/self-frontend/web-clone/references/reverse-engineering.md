# 逆向 WebGL / Canvas

侦察到 `window.THREE`、多个 `<canvas>`、或 `type="x-shader/*"` 时用。证据纪律见 `effect-extraction.md`。

1. 先拿单文件源码（GitHub raw / 查看源代码），别急着抓站。
2. 数 canvas、读 SVG `defs`、grep shader。
3. 判断 WebGL 在算什么：
   - `texture2D` / `sampler2D` → 采样纹理 / FBO
   - 循环里 `+= dS` / `map(` / `MAX_STEPS` → ray-marching
   - `b*b` / 判别式 / `sqrt(` + 二次方程 → 解析求交（球/平面常见）
   - 别默认假设折射 demo 用 ray-marching。
4. 找 GPU↔DOM 桥：`toDataURL` / `<feImage>` / `feDisplacementMap` → 在生成数据图给别的层，不是直接显示。
5. 物理 / 音频通常是解耦的纯 JS，可单独验证。

可迁移范式：位移图折射真 DOM（SVG `feDisplacementMap`，Three.js `transmission` 做不到）；一套 shader + `u_mode`；辅助图降分辨率 + 静止跳帧；全屏大三角。

路径：许可允许则拿真源码改内容；近似则找同类开源，但先确认有没有丢掉原站灵魂机制（如「折射真 DOM」）。形状/材质变了，求交公式和魔数要重写。

验证：本地起服 → `playwright-cli` 打开 → console 无 JS/WebGL 编译错误 → 截图对照。拖拽若依赖 `isTrusted`，如实写入 NOTES。
