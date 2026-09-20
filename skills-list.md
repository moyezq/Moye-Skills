> 归纳日期：2026-09-20

# 个人 Skills 清单

给人看的薄索引。Agent **何时读哪份正文** 以会话索引 [`self-session-bootstrap`](./skills/self-session-bootstrap/SKILL.md) 的路由表为准，这里不复述触发条件。

正文在 `skills/`。各产品目录联接见根目录 `README.md` 与 `.env.example`。

术语与决策见 [`CONTEXT.md`](./CONTEXT.md)。共 **18** 个个人 skill。仅一端会读的 skill 仍在这份树里，靠路由表约束。

## 会话与规范

| Skill | 一句话 |
|-------|--------|
| `self-session-bootstrap` | 会话索引：开场读路由表并做开场对齐；命令/conda 日探测用到才触发 |
| `self-code-principles` | 代码设计默认原则（12 条，跨语言兜底） |

## Python 与项目

| Skill | 一句话 |
|-------|--------|
| `self-python-style` | 本机 Python 风格与第一次怎么跑 |
| `self-python-function` | 函数 / 类 / FastAPI 路由怎么写 |
| `self-python-script` | 单文件分阶段脚本（stepN、参数硬编码） |
| `self-python-project` | 目录归档、案例形态、小服务怎么摆 |
| `self-react` | React 页面 / 布局 / 界面验收（Vite + TS） |

## 知识库

| Skill | 一句话 |
|-------|--------|
| `self-notes-read` | 笔记库 查阅、整理、书写 |

## 对齐与建模

| Skill | 一句话 |
|-------|--------|
| `grilling` | 拷问式访谈原语（设计树 + 前沿 + 轮次） |
| `grill-with-docs` | 边对齐边沉淀 CONTEXT / ADR（用户手动触发） |
| `domain-modeling` | 项目术语表 CONTEXT.md 与 ADR |

## 调试、调研、表达

| Skill | 一句话 |
|-------|--------|
| `research` | 后台调研，产出带引用的 Markdown |
| `show-me` | 用树 / Mermaid / diff 等可视化讲清结构 |
| `playwright-cli` | 浏览器自动化与 Playwright CLI 调试 |
| `web-clone` | 网站复刻：真源码 → 判路径 → 搭工程 |
| `cli-service-desktop-shortcut` | 命令行服务做成 Windows 桌面快捷方式 |

## Skill 自身

| Skill | 一句话 |
|-------|--------|
| `skill-creator` | 新建 / 改 skill、跑 eval |
| `writing-for-agents` | 写 agent 会读的文档（skill、规范文件） |

## 官方 Skills

来源：`~\.cursor\skills-cursor\`。以对话 `available_skills` 为准，description 命中再读，开场不预加载。
