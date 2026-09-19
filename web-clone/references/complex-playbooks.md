# L4–L6 playbook

## L4 动画品牌站

`recon-site` 三档截图。记 GSAP / Lenis / ScrollTrigger / Locomotive。拆首屏、滚动叙事、视频蒙版、hover、过渡。优先节奏和视觉语法；微交互可近似，差异写入 `CLONE_REPORT.md`。`visual-diff` 评首屏和关键滚动位。

## L5 WebGL / Canvas / Three

先找源码 / source map。`recon-site` 记 canvas。`sourcemap-hunt`。拆渲染、shader、后期、物理、交互、音频、加载。复杂 shader 先最小可运行再补。交互必须有浏览器证据。

## L6 SaaS / 电商 / 登录

默认只克隆展示层。确认授权后再碰登录态页。`network-capture` 做 fixtures。内容接口 → 本地 JSON；交易/写入 → mock 成功/失败。保留空态 / 加载 / 错误 / 权限不足。`audit-clone` 扫外链和原品牌。

## 多页 / CMS

先 sitemap、导航、页脚、模板。只复刻代表页：主页、列表、详情、筛选、联系。重复内容用数据文件。后台不克隆。

## 完成

原站证据齐；克隆可本地跑，error 清零或已解释；`CLONE_REPORT.md` 有分；`CLONE_AUDIT.md` 无未解释的追踪/品牌/外链风险；做不到的后端与版权写进边界。
