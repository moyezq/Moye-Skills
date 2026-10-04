---
name: self-frontend
description: >
  前端开发入口。写或改页面、布局、React、Vite、TypeScript、界面验收、
  仿站、克隆网页、抄个站时查阅。读完按本文再读其下 self-react 或 web-clone。
  点选走查走 self-spyder。不要用本文件还原接口签名。
---

# 前端

个人前端的入口。本文件只分流，不复述细则。

完成标准：已按「再读哪份」打开对应正文；没有用本文件代替那两份执行。

## 何时用 / 何时不用

**用**：写或改前端页面 / 布局 / 样式；React（默认 Vite + TypeScript）；界面验收；按网页前端样式复刻（克隆 / 仿站 / 抄个站）。

**不用**：后端接口；纯事实查询；可交互分析面板走官方 `canvas`；只做页面点击走查走 `self-spyder`，不必先读本文。写 `.py` 走 Python 那几份。

## 再读哪份

两份整目录在本 skill 下，正文不改。入口文件叫 `BODY.md`（不能叫 `SKILL.md`，否则 Cursor 会当成独立 skill 列出来）。按任务读，可两份都读。写或改前端代码仍加读 `self-code-principles`（与 `self-react` 冲突点以 `self-react` 为准）。

| 目录 | 管什么 | 何时 Read 正文 |
|------|--------|----------------|
| [`self-react/`](./self-react/BODY.md) | React 页面、布局、界面验收 | 加页面、改布局、调滚动、联调、镜像类型、验收；dev server 像旧代码 |
| [`web-clone/`](./web-clone/BODY.md) | 按网页前端样式、交互、WebGL 复刻 | 克隆 / 仿站 / 抄个站；先拿真源码。不要用那份还原 `sign` 或对照协议 |

`web-clone` 的脚本在其自己的 `scripts/`（那份里的 `$S`）。

## 受限沙箱下的构建门禁

`npx vite build` 会 `spawn EPERM`——esbuild 要起一个带管道 stdio 的子进程，而受限沙箱禁止命名管道。类型门禁
`npx tsc --noEmit` 不受影响，先跑它；要跑构建就按沙箱规矩对**同一条命令**提权重试一次（`sandbox_permissions`），
不要改写成别的命令绕开。
