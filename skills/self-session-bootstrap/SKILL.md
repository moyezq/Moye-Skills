---
name: self-session-bootstrap
description: 会话索引：对话开场必须加载的个人 skills 路由。新对话第一条用户消息、本对话尚未读过本 skill、或用户说「先读规范 / 先看 skills」时必须作为第一步查阅。开场只读本文、记住路由表、做开场对齐；系统命令与 conda 日探测用到才触发。Python 风格见 self-python-style。禁止开场通读全部 skill；后续轮次已读过则不必重读。
---

# 对话开场：硬约束 · 路由表

本 skill 是 **会话索引**，不是某个具体任务的写法。读完按用户这一轮的任务继续；不要向用户复述路由表或环境卡全文，除非对方在问规范本身。

后续轮次：本对话里已经读过就不要再 Read 一遍。

---

## 1. 开场要做什么

本对话只做一次：读完本文件，记住第 4 节路由表，然后做开场对齐。不读环境卡、不预读其它 skill。

工作树 = 本 skill 根目录的父目录（即 `skills/`）。仓库根用 `git -C "<skill根目录>" rev-parse --show-toplevel` 取得。换电脑后 fullPath 会变，不要写死盘符。

开场完成：已读本文、记住路由表、开场对齐已执行或已跳过。其它 skill 等本轮任务命中再第一次 Read。写或改 `.py`、或本对话第一次要为任务跑 Python 时加读 `self-python-style`。任务涉及 `笔记库` 知识库 `.md` 时加读 `self-notes-read`。

不要：把 `available_skills` 里每一份正文都读一遍；不要因为「首次对话」去打开 Figma / Canvas / SDK 等产品 skill。

### 开场对齐

在仓库根执行。`git fetch` 失败（还不是 git 仓库、网络不通、没有 git）则跳过，用本地继续。

```powershell
$repoRoot = git -C "<skill根目录>" rev-parse --show-toplevel
git -C $repoRoot fetch
```

fetch 成功后按顺序只走一条：

1. `git -C $repoRoot status --porcelain` 有输出 → 向用户报告 dirty，结束开场对齐。
2. `git -C $repoRoot rev-list --left-right --count HEAD...@{u}` 得到 ahead（左）与 behind（右）。没有上游则跳过。
3. behind>0 且 ahead=0 → `git -C $repoRoot pull --ff-only`。失败则报告，结束开场对齐。
4. ahead>0 且 behind=0 → 问用户是否 push，等确切回复。本步不 push、不 commit。
5. ahead>0 且 behind>0 → 向用户报告分叉，结束开场对齐。
6. 都是 0 → 不说话，继续本轮任务。

---

## 2. 整个对话必须遵循的硬约束

只放跨任务、且没有更专门 `self-*` 承接的进程/环境规则。脚本入口见 `self-python-script`；风格与怎么跑见 `self-python-style`；产物目录见 `self-python-project`；注释与代码判断见 `self-code-principles`。

- 用中文回答。
- 默认环境 Windows；默认编程语言 Python。写 `.py` 或第一次要为任务跑 Python 时读 `self-python-style`。
- 验证由用户手动执行；AI 只做静态审查和逻辑说明。不要运行 `test_*.py`、`.sh`、`.bat` 以及业务入口脚本做验证。
- 任务结束后不主动新建说明用 `.md`。用户明确要求、或更新与任务相关的 README / docstring / 阶段注释除外。
- 删模块、改配置路径、换入口后，在回复中请用户重启服务再手动验证；勿把仍在跑的旧进程当成新代码已通过。
- Windows 改多文件以写盘内容为准核对。

---

## 3. 环境卡与白名单

OS：Windows。Shell：PowerShell。探测脚本只随本 skill 提供，**不要**去工作区、笔记目录或其它磁盘路径找。本 `SKILL.md` 所在目录就是 skill 根目录（`available_skills` 里本 skill 的 fullPath 的父目录）。换电脑后 fullPath 会变，不要写死盘符。

环境卡：`scripts/_meta/env_card.json`。对照对话里的今天，写成 `YYYY-MM-DD` 再和卡上日期比。stdout 字段以脚本为准，不要猜、不要补。

探测前允许：Cursor 工具、conda、PowerShell 内建。PATH 上的 `pip` 不用于装包。开场对齐允许 `git fetch`、`git status --porcelain`、`git rev-list`、`git pull --ff-only`，不先读环境卡。

### 系统命令日探测

本对话第一次需要白名单 PATH 命令时：Read 环境卡（没有当过期）。`commands_date` 等于今天则用卡里的 `commands`。否则：

```powershell
conda run -n base python "<skill根目录>/scripts/env_detect.py"
```

固定 base，不读 conda 环境名单。这不是为任务跑 Python。要增删命令只改该脚本顶部 `COMMANDS_TO_CHECK`。当天 `commands_date` 已是今天则不要再跑。

### conda 环境名

第一次为任务跑 Python 时见 `self-python-style`。探测脚本不算这次触发。不要开场跑 `conda env list` / `pip list`。

### 白名单

| 允许 | 不允许 |
|------|--------|
| Cursor 工具：Read / Write / Grep / Glob / Shell | 把 Shell 当探测器反复 which |
| 环境卡当天 `commands` 里的名字 | 名单里未出现在当天 `commands` 的命令（不要点名罗列） |
| `conda`（`conda run`；conda 环境名见 `self-python-style`） | 开场跑探测、开场读环境卡 |
| 开场对齐的 `git fetch` / `status --porcelain` / `rev-list` / `pull --ff-only` | `commands_date` 已是今天时再跑 `env_detect.py` |
| PowerShell 内建（配合读写文件） | 开场对齐里 `commit` / `push` / `merge` / `rebase` |

`commit` / `push` 以环境卡当天 `commands` 含 `git` 且用户明确要求时才用，并遵守用户 git 规则。

---

## 4. 路由表

目录里永远能看到 name + description。这张表决定 **什么时候才读正文**，是 agent 的单一事实源。人读分组见仓库根目录 `skills-list.md`，不要把那份当路由。

| Skill | 管什么 | 何时 Read 正文 |
|-------|--------|----------------|
| `self-session-bootstrap` | 本文件：开场、白名单、路由 | 新对话第一步；已读过则停 |
| `self-code-principles` | 代码设计 12 条兜底 | 写/改代码（有更专门 self-* 仍读，冲突点让位）；问基本原则 |
| `self-python-style` | Python 风格与怎么跑 | 写或改 `.py`；或本对话第一次要为任务跑 Python |
| `self-python-function` | 函数 / 类 / 路由怎么写 | 改 def、class、工具函数、FastAPI 路由；嫌拆太碎 |
| `self-python-script` | 分阶段脚本切步 | 目标已定、一个 `.py`、按数据跳写 `stepN` |
| `self-react` | React 页面 / 布局 / 界面验收 | 加页面、改布局、调滚动、改联调、界面验收；dev server 像旧代码 |
| `self-python-project` | 目录、归档、小服务形态 | 整理项目、改目录、归档案例、组织小服务；嫌拆太多 |
| `self-notes-read` | 笔记库 查阅 / 整理 / 书写 | 读/写/改库 `.md`、入门文、批量整理、外部文档、课件转笔记 |
| `skill-creator` | 写 / 改 skill、eval | 用户要新建或修改 skill |
| `playwright-cli` | 浏览器自动化与 Playwright CLI | 用户提到 playwright-cli、页面快照、UI 走查；整站复刻走 web-clone |
| `web-clone` | 网站复刻：真源码 → 判路径 → 搭工程 | 复刻/克隆/仿站/还原网页或 WebGL 效果 |
| `grilling` | 拷问式访谈 | 压力测试、对齐需求；说拷问/盘问/对齐 |
| `domain-modeling` | CONTEXT.md + ADR | 讨论术语；写改 CONTEXT.md、记 ADR |
| `grill-with-docs` | 拷问并建文档入口 | 用户要边对齐边沉淀术语/决策 |
| `research` | 后台调研 | 调研话题、查文档/API 事实 |
| `writing-for-agents` | 写 agent 文档 | 写/改 skill、优化 description、写规范文件 |
| `show-me` | 可视化讲清结构 | 画一下 / 示意 / 数据流 / show me |
| `cli-service-desktop-shortcut` | 命令行服务做成桌面快捷方式 | 桌面快捷方式、双击启动、把服务做成图标 |

写代码默认加读 `self-code-principles`，有更专门 `self-*` 则那份优先。对齐用 `grilling`；沉淀术语用 `grill-with-docs` + `domain-modeling`。细节以各 skill 自己的「何时用 / 何时不用」为准。

产品自带 skill（Canvas、Figma、Cursor SDK 等）：以本对话 `available_skills` 为准，**任务 description 命中再读**，开场不预加载。

新 skill 加入或改名/停用时：改这张表，并改对应 description 里的交叉引用；旧名不要留在表里。
