---
name: web-clone
description: >
  网站复刻方法论。用户说复刻网站、克隆网站、clone website、抄个站、仿站、
  照着这个站做一个、reproduce site、还原某个网页效果、把这个站搬下来改成我的、
  复刻某个交互/WebGL/Canvas/Three.js 效果时用。先拿真源码再判路径。
  验收自己写的 React 页走 self-react；只做页面点击走查走 playwright-cli。
---

# 网站复刻

- 脚本：本 skill 根目录下的 `scripts/`（下称 `$S`）
- 克隆根（下称 `$R`）：先问用户确认路径，确认后再建。不要默默 mkdir。

AI「复刻分析」里的可执行代码默认臆造，必须逐行对真源码。反例见 `references/marbles-case.md`。

## 0 建工程

确认克隆根存在后：

```
node $S/init-clone.mjs <站名> --url <原站URL>
```

## 1 先搜 GitHub 源码

```
gh api "search/repositories?q=<关键词>"
```

许可允许 → 跳第 4 步直接 clone。单文件 github.io → 拉 raw `index.html`。

## 2 没源码 → 侦察

公开站 / localhost 用下列脚本（内置 Playwright）。人眼核对读 `playwright-cli`。缺 Playwright：在 `$R` 里 `npm install -D playwright`。参数细节跑 `node $S\<脚本> --help`。

| 脚本 | 作用 |
|------|------|
| `recon-site.mjs` | 框架 / DOM / 三档截图 → `$R\RECON`，`--label original` |
| `asset-harvest.mjs` | 按下 recon JSON 下素材 |
| `network-capture.mjs` | SPA/SaaS 的 XHR/fetch fixtures |
| `route-crawl.mjs` | 多页路由图（默认 `--max-pages 25 --max-depth 2`） |
| `interaction-probe.mjs` | hover / click / scroll / canvas drag |
| `sourcemap-hunt.mjs` | 从 JS chunk 找 source map |

## 2.5 定级

按 `references/assessment.md` 写预判：L1–L6、模式、可还原范围、明确不克隆的部分。

视觉复刻 / 内容爆改才跑 `dna-scaffold.mjs` 出 `design-dna.json`（`references/design-dna.md`）。忠实复刻不用 DNA。

## 3 选路

| 侦察 | 路径 |
|------|------|
| 静态 HTML/CSS | `mirror-site.mjs` → 删追踪 → 改文案 |
| React / Vue / Next 内容站 | 重建模板灌内容 |
| SPA / SaaS | `network-capture` → 本地 JSON/mock |
| 多页官网 | `route-crawl` → 每类抽模板 |
| 复杂交互 | `interaction-probe`，禁止只截首屏 |
| WebGL / Canvas / Three.js | 真源码逆向；无源码则帧捕获 + 闸门。`references/reverse-engineering.md`、`references/effect-extraction.md` |
| 静态构建（Astro / Vite SSG / Hugo），含重 WebGL | `mirror-site.mjs` 1:1。`references/static-mirror.md` |
| 现成开源主题 | 主题市场找源主题；定制站走镜像，不走市场 |

L4–L6 走 `references/complex-playbooks.md`。

## 4 搭工程

源码放进 `$R`。留只读 `index-original.html`。按 `package.json` `engines` 选 Node。

## 5 删追踪 + 产物 + 验证

删 GA / gtag / 像素。写 `NOTES.md`（必须）。复杂站加 `TEARDOWN.md`，结论标行号。评分见 `references/assessment.md`。产物模板见 `references/deliverables.md`。

本地起服 → 用 `playwright-cli` 打开 → console 无 JS/WebGL 编译错误 → 截图对照。合成 PointerEvent `isTrusted=false` 拖不了就如实记。

再对克隆站跑 `recon-site` / `route-crawl` / `interaction-probe`（`--label clone`），然后：

- `compare-recon.mjs` → `CLONE_REPORT.md`
- `visual-diff.mjs` 对比 1440 截图
- `audit-clone.mjs` → `CLONE_AUDIT.md`

## 6 换成你的内容

换文字、媒体、品牌色。有 DNA：DNA 留着、内容换掉。结构非平凡写 `REPLACE_GUIDE.md`。

## 许可

clone 前：`gh api repos/<u>/<r>` 看 `.license`，并打开 LICENSE 文件。

| 许可 | 可做 |
|------|------|
| MIT / Apache / BSD / Unlicense | 可改可上线，留致谢 |
| 未声明 | 默认保留所有权利。仅本地学习，未许可不公开部署 |
| 专有 / 禁止 | 只读学习 |

公开仓库 ≠ MIT。

## 边界

- 高保真：静态营销页、内容型 React/Vue/Next、有源码的动画站
- 可视觉近似：CMS 数据、复杂滚动、WebGL、第三方嵌入
- 不承诺：登录、支付、下单、推荐、权限、服务端逻辑、专有 API、受版权素材（需要时只做演示替身）
- 内容爆改：留信息架构 / 节奏 / 动效 / 视觉语法，换文案、图片、品牌主张
