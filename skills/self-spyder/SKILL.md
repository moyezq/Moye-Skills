---
name: self-spyder
description: >
  浏览器自动化入口。用户提到 playwright-cli、页面快照、UI 走查、
  录屏、tracing、请求 mock、npx playwright test --debug=cli、
  网页点击填表时查阅。读完再读其下 playwright-cli。整站复刻/仿站走 self-frontend。
---

# 浏览器自动化

入口。本文件只分流，不复述 CLI 细则。

完成标准：已打开其下 `playwright-cli` 正文；没有用本文件代替那份执行。

## 何时用 / 何时不用

**用**：浏览器自动化、网页点击填表、页面快照、Playwright CLI、UI 走查、录屏 / tracing、请求 mock。

**不用**：整站复刻 / 仿站走 `self-frontend`。写页面 / 布局 / 验收走 `self-frontend`（其下 `self-react`）。

## 再读哪份

整目录在本 skill 下，正文不改。入口文件叫 `BODY.md`（不能叫 `SKILL.md`，否则 Cursor 会当成独立 skill 列出来）。

| 目录 | 管什么 | 何时 Read 正文 |
|------|--------|----------------|
| [`playwright-cli/`](./playwright-cli/BODY.md) | Playwright CLI 驱动浏览器、快照、走查、生成测试 | 本入口命中后都读这一份 |
