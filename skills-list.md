> 归纳日期：2026-10-07

# 个人 Skills 清单

给人看的薄索引。Agent **何时读哪份正文** 以对话里 `available_skills` 的 description 为准，这里不复述触发条件。命令 = `/` + skill 名。

正文在 `skills/`。各产品目录联接见根目录 `README.md` 与 `.env.example`。

术语与决策见 [`CONTEXT.md`](./CONTEXT.md)。共 **18** 个个人 skill。仅一端会读的 skill 仍在这份树里，靠各自的 description 约束。

暂存（不进工作树）：`backup/` 下的 `apk-reverse`、`js-reverse`、`protocol-reverse`、`research`、`cli-service-desktop-shortcut`、`caveman`、`skill-creator`、`writing-for-agents`、`find-skills`、`skill-crud-eval`（对照实验那套：评审与复盘子代理 brief、观测台脚本）。

## 会话与规范

| Skill | 一句话 |
|-------|--------|
| `self-session-bootstrap` | 会话索引：开场七步（判 Agent / 系统 / skill 根目录、系统命令白名单、conda 环境、按 Agent 读 harness 操作规范）、全程约束、输出要求 |
| `self-session-handoff` | 会话交接：写交接文档给下个会话，或从交接接着干（一个指针，一份活着的交接） |
| `self-session-audit` | 自检本轮会话：工具调用/真失败/重复调用统计、token 与上下文占用、skill 是否真加载 |
| `self-code-principles` | 代码设计默认原则（跨语言兜底） |

## Python 与项目

| Skill | 一句话 |
|-------|--------|
| `self-python-style` | 本机 Python 风格与第一次怎么跑 |
| `self-python-function` | 函数 / 类 / FastAPI 路由怎么写 |
| `self-python-script` | 单文件分阶段脚本（stepN、参数硬编码、顶部注释） |
| `self-python-project` | 目录归档、案例形态、小服务怎么摆 |
| `self-python-testing` | 定缝 → 写进 spec → 写 pytest；上游 `tdd` / `to-spec` / `python-testing-patterns` 三份的中文组合 |

## 前端

| Skill | 一句话 |
|-------|--------|
| `self-frontend` | 前端入口：其下 `self-react`（页面/布局/验收）、`web-clone`（按真源码复刻） |

## 桌面

| Skill | 一句话 |
|-------|--------|
| `self-desktop-ui` | Windows 桌面壳界面：窗口/材质/输入/密度/动效 + 上线审计（WebView2 / Electron / Tauri） |

## 知识库

| Skill | 一句话 |
|-------|--------|
| `self-notes-read` | 笔记库 查阅、整理、书写 |

## 对齐与建模

| Skill | 一句话 |
|-------|--------|
| `grill-with-docs` | 拷问式访谈（设计树 + 前沿 + 轮次），结晶了按落点沉淀文档 |
| `self-project-docs` | 项目术语表、ADR、蓝图、文档地图、最小视图 |

## 工具

| Skill | 一句话 |
|-------|--------|
| `self-spyder` | 浏览器自动化入口：其下 `playwright-cli` |
| `self-interview-question` | 把开发经历抽成可迁移的面试题 |

## Skill 自身

| Skill | 一句话 |
|-------|--------|
| `self-skill-crud` | 个人 skill 的增删改查（建 / 改 / 删 / 找）：共用判据 + 四份流程；模型按边界自动够到，不挂命令 |
| `skill-analyse` | 分析上游/本地 skill，写成 analyse 报告（用户触发 `/skill-analyse`） |

## 官方 Skills

来源：`~\.cursor\skills-cursor\`。以对话 `available_skills` 为准，description 命中再读，开场不预加载。
