# 产物

每个复刻：`<工作区根>\Clone\<站名>-clone\`。

## NOTES.md（必须）

```markdown
# <站名> · 克隆笔记

## 源信息
- 原站 URL:
- 源码仓库:
- 原作者:
- 许可证: MIT / Apache / NONE / 专有
- 致谢要求:

## 技术栈
- 框架 / 关键库 / Node 版本:

## 复刻前预判
- 复杂度等级: L1–L6（见 assessment.md）
- 推荐模式: 忠实复刻 / 视觉复刻 / 内容爆改 / 技术拆解
- 可高保真 / 需近似 / 不克隆 / 主要风险:

## 跑起来
cd <工作区根>\Clone\<站名>-clone
python -m http.server 8123

## 改了什么
- 删了追踪脚本:（GA/gtag 行号）

## 原站 vs 克隆站
| 模块 | 原站 | 克隆 | 差异 | 证据 |
|------|------|------|------|------|
| 首屏 / 导航 / 核心动效 / 内容区块 / 移动端 |  |  |  | screenshot / file:line |

## 复刻评分
源证据 / 结构 / 视觉 / 动效 / 响应式 / 功能 / 内容替换 / 法务：各 /5。总评:

## 替换地图
文字 / 媒体 / 配色 / 模型字体 → 文件或目录

## 验证
- [ ] 本地跑通、console 0 error
- [ ] 截图对照 `RECON/screenshots/`
- [ ] 多页：`route-crawl` 原/克路由图
- [ ] 交互站：`interaction-probe` 状态证据
- [ ] `visual-diff`（能做时）
- [ ] `audit-clone`
- 验证不了的点（如实记）:
```

## TEARDOWN.md（复杂交互站）

结论标真源码行号 + `SOURCE` / `PARTIAL` / `GUESS`（见 `effect-extraction.md`）。

- 0. 一句话本质
- A. 按支柱拆：渲染 / 合成 / 物理 / 交互 / 音频
- B. 若有 AI 分析：`声称 | 真源码 | ✅/⚠️/❌ | 说明`
- C. 可迁移套路 vs 本站特有 vs 复刻路径

## RECON/

- `screenshots/original-{1440,768,390}.png`、`clone-1440.png`、`visual-diff-1440.png`
- `original-recon.json` / `clone-recon.json`
- `routes/`、`routes-clone/`、`interactions/`、`interactions-clone/`
- `asset-manifest.json`、`network/`、`sourcemaps/`、`visual-diff-1440.json`
- 视觉/爆改：`design-dna.json`
- WebGL 逆向：`baseline/`（最小原样可复现）

## CLONE_REPORT.md（评估时）

结论（等级 / 模式 / 还原度 / 用途）+ 信息架构 / 视觉 / 动效 / 响应式 / 内容 / 功能边界对比 + assessment 八项分数 + 缺口。

## CLONE_AUDIT.md（上线前）

`audit-clone.mjs` 生成。看追踪脚本、原品牌/语言残留、外链、license。

原始源码留只读 `index-original.html`。
