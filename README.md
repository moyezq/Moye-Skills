# Moye-Skills

一套个人向的 **Agent Skill** 库：把「怎么判断、怎么做」写成可复用的规范，一次编写，Cursor / dsh / Codex 三端共用。

Markdown 为主 · 无运行时依赖 · 目录联接共用一份正文 · 个人分享

## 页内目录

[介绍](#介绍) · [快速开始](#快速开始) · [怎么工作](#怎么工作) · [项目结构](#项目结构)

## 介绍

Agent Skill 是给 AI 读的规范：命中任务时它被读进上下文，替掉每次重讲一遍的口头约定。本仓把这些规范按作用域拆成 12 份，每份只管一层——会话怎么开场、代码怎么写、文档落在哪、需求怎么问清。

三端共用靠**目录联接**，不是拷贝：`setup.ps1` 把 Cursor / dsh / Codex 各自的个人 skills 目录指向本仓 `skills/`，所以只有一份正文，改一处三端同时生效。

| 能力（skill） | 做什么 | 不装会怎样 |
|---|---|---|
| `session-bootstrap` | 新对话开场七步：判当前 Agent、系统、skill 根目录、可用命令与 conda 环境，定这一轮的全局约束 | 每个会话都要重新交代工具与约定 |
| `code-principles` | 13 条跨语言代码判断，写改代码时兜底 | 没有兜底原则，AI 按各自默认口味写 |
| `python-standard-coding` | Python 写法与落盘：风格、类型、函数、容器、性能、脚本、多文件目录 | Python 风格与目录随对话漂 |
| `python-testing` | 先选定测试边界，再写进 spec，最后按一条用户路径写 pytest | 测试写了也不知道该测哪一层 |
| `project-docs` | 项目文档：术语表、ADR、人读 README、文档地图、最小视图 | 术语和决策没有落点，反复问同一件事 |
| `grill-with-docs` | 拷问式访谈：按轮次只问当前前沿能答的，边问边沉淀文档 | 需求没对齐就开写，返工 |
| `plain-todo` | 用白话把一项待办讲清再执行 | 待办含糊，动手后才发现没想清 |
| `playwright-cli` | 浏览器自动化：点击填表、页面快照、UI 走查、录屏/tracing、请求 mock、生成测试 | 界面验收只能靠人截图描述 |
| `skill-crud` | 个人 skill 的增删改查（建 / 改 / 删 / 找）与 skill 文本规范 | 改 skill 容易破坏单一事实源、漏改连带文件 |
| `skill-analyse` | 把上游或本地的 skill 拆成 analyse 分析报告 | 想收编别人的 skill 时得自己啃源码 |
| `session-tools` | 本轮会话自检、写交接文档、抽可迁移面试题 | 长会话丢了上下文，只能从头重讲 |
| `self-notes-read` | 查阅、整理、书写 Markdown 知识库（要配 `NOTES_ROOT`） | 笔记不按统一框架进库，沉淀不下来 |

## 快速开始

### Ⅰ 装上并跑通（必需，约 5 分钟）

```powershell
git clone git@github.com:moyezq/Moye-Skills.git
cd Moye-Skills
copy .env.example .env
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

`.env`（模板 [.env.example](.env.example)）这一步只管三个产品目录——它们是整套机制的唯一输入：

| 键 | 是什么 | 装在默认位置时 |
|---|---|---|
| `CURSOR_SKILLS` | Cursor 扫个人 skill 的目录 | `%USERPROFILE%\.cursor\skills` |
| `DSH_SKILLS` | dsh 扫个人 skill 的目录 | `%USERPROFILE%\.dsh\skills` |
| `CODEX_SKILLS` | Codex 扫用户级 skill 的目录 | `%USERPROFILE%\.agents\skills` |

`setup.ps1` 把这三个目录各做成指向本仓 `skills/` 的**目录联接**（同名目录已存在就先备份成 `<名字>.bak-<日期>`；联接指向别处则重建）。某个产品没装就把它留空，那一项会被跳过。看到 `ok <产品目录> -> <本仓>\skills` 就是接上了，然后**重启 Cursor / dsh**——目录联接只在启动时读一次。

验收：新开一个对话，问「这段代码还能怎么简化」。`code-principles` 应当被读到，并按那 13 条回答。

### Ⅱ 配齐完整能力（让 Agent 自己填）

这几项都是「本机上有什么」的事实，不用你自己查：开一个新会话，让 Agent 跑一遍本地探测，按实情写进 `.env`。都不影响 Ⅰ 能不能跑通。

| 键 | 是什么 / 配了能做什么 | 没配会怎样 |
|---|---|---|
| `GITHUB_PAT` | fine-grained PAT，权限 `Contents: Read and write`；dsh 会话里可自行 fetch / pull / push | 远端 git 操作交你自己的终端 |
| `NOTES_ROOT` | 你的 Markdown 笔记库根目录，`self-notes-read` 用 | 这份 skill 拿不到库路径 |
| `NPM_CACHE` | npx 缓存目录，`skill-crud` 的取源脚本用 | 回落到 `WORKSPACE_ROOT` 下的 `.npm-cache` |
| `SKILLS_ROOT` / `WORKSPACE_ROOT` | 本仓根 / 本仓所在的那一级目录。skill 正文不写死盘符与用户名，要用绝对路径就取这两个键 | 只少一条路径来源，不报错 |

### Ⅲ 试一次（三条真实触发）

1. 新开会话，第一句话说任意内容 —— `session-bootstrap` 先做开场，报出当前 Agent、系统与工作目录。
2. 说「先问清楚再动手」—— `grill-with-docs` 按轮次提问，每轮只问当前前沿能答的。
3. 说「用浏览器把这一步点一遍」—— `playwright-cli` 驱动浏览器并留下快照。

触发全靠各 skill 的 `description`：命中就读，没命中就直接点它的名字。

## 怎么工作

```mermaid
flowchart LR
  A[新对话] --> B[session-bootstrap 开场]
  B --> C{这一轮是什么活}
  C -->|写改代码| D[code-principles 兜底<br>python-standard-coding / python-testing]
  C -->|文档与术语| E[project-docs]
  C -->|需求还没对齐| F[grill-with-docs]
  C -->|动 skill 本身| G[skill-crud]
```

- **一份正文，三端共用**：正文只有 `skills/` 一棵树；三端各扫自己那个个人 skills 目录，而那三个目录都是指向本仓 `skills/` 的目录联接——改一处三端同时生效，不存在第二份拷贝。
- **触发靠 description，材料靠指针**：`description` 常驻在对话目录里，命中才读正文；正文只留每条路径都要的步骤，细则推到 `references/` 按需读。
- **开场只有一份**：`session-bootstrap` 决定这一轮按哪套工具干活，其余 skill 不在开场预加载。
- **叫法与决策有落点**：规范名称进 `CONTEXT.md`，仍有效的为什么进 `docs/adr.md`，废掉的追加 `docs/HISTORY.md`。

## 项目结构

```text
Moye-Skills/
├── README.md          # 你正在读的这份
├── setup.ps1          # 把三端个人 skills 目录联接到本仓 skills/
├── .env.example       # 本机配置模板，复制成 .env 再填
├── skills/            # 工作树：12 份 skill 的正文，三端共用
├── skills-list.md     # 薄索引：一行一个 skill
├── CONTEXT.md         # 术语表：本系统特有叫法的规范名称
├── docs/              # 内部说明，日常使用不必读
└── preinstall/        # 上游 skill 取源暂存区，等人审
```
