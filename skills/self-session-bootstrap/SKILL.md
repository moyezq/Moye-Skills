---
name: self-session-bootstrap
description: 会话索引：对话开场必须加载的个人 skills 开场规矩与全局约束。新对话第一条用户消息、本对话尚未读过本 skill、或用户说「先读规范 / 先看 skills」时必须作为第一步查阅。开场读本文、判当前 Coding Agent。系统命令日探测用到才触发。命令：/self-session-bootstrap
---

# 会话索引

本文件不是某个具体任务的写法。四块：§1 开场一次，§2 全程约束，§3 用到才做，§4 输出要求。读完按用户这一轮的任务继续；不要向用户复述环境卡全文，除非对方在问规范本身。

---

## 1. 开场

本对话只做一次，按序：

1. 读完本文件。
2. 通过已注入的系统提示词，判断当前 Coding Agent（`dsh` / `cursor` / `codex` / 其它），记作 `AGENT`。
3. 判当前系统，取最省的一步：

   - 工具集里有 `pwsh` → Windows；有 `bash` → Linux / macOS
   - Windows 要硬确认跑 `$IsWindows`；Linux / macOS 跑 `uname -s`（Linux / Darwin）

开场只做这三步。环境卡、日探测、conda / pip 列表、git 在第 3 节，触发了再做。其它正文：用到才读，读过不重读。

---

## 2. 全程约束

只放跨任务、且没有更专门 skill 承接的规则。

- 用中文回答。
- 可独立完成的简单、确定多步活优先派 SubAgent；一眼能查的用本对话工具，不派。主问题仍在本对话做。
- 默认环境 Windows；默认编程语言 Python。
- 验证由用户手动执行；AI 只做静态审查和逻辑说明。不要运行 `test_*.py`、`.sh`、`.bat` 以及业务入口脚本做验证。用户本轮明确要求「跑通再写入文档 / 验证真实可用」时，可以跑该入口脚本；测完停掉自己拉起的服务。
- 任务结束后不主动新建说明用 `.md`。用户明确要求、或更新与任务相关的 README / docstring / 阶段注释除外。
- 删模块、改配置路径、换入口后，在回复中请用户重启服务再手动验证；勿把仍在跑的旧进程当成新代码已通过。
- Agent 为探测或联调后台起的服务（HTTP、向量、Vite）测完立刻停掉，不要常驻占端口。用户终端里已在跑的进程不要杀。
- Windows 改多文件以写盘内容为准核对。

---

## 3. 用到才做

每小节 = 触发条件 + 按序步骤。探测脚本只随本文件提供。

skill 根目录 = 加载本文件时给出的那个目录：
- Cursor 看 `available_skills` 里本文件 fullPath 的父目录
- dsh 看「Base directory for this skill」那行。

命令与路径随系统走，不写死盘符。

### 系统命令日探测

本对话第一次要用白名单 PATH 命令时：

1. Read `scripts/_meta/env_card.json`。没有文件当过期。
2. 把今天写成 `YYYY-MM-DD`，和卡上 `commands_date` 比。相同则用卡里的 `commands`，停。
3. 不同则跑：`conda run -n base python "<skill根目录>/scripts/env_detect.py"`。固定 base。stdout 字段以脚本为准，不要猜、不要补。
4. 当天已经跑过则停。

增删命令只改该脚本顶部 `COMMANDS_TO_CHECK`。这不是为任务跑 Python。

### 白名单

Shell 里要用第三方命令时：

1. 先完成「系统命令日探测」（当天只做一次）。
2. 名字在环境卡当天 `commands` 里 → 用；不在 → 不用，也不点名罗列缺什么。
3. `conda` 始终可用：探测用 `conda run -n base`；业务启动用 `conda activate` 再 `python`。PATH 上的 `pip` 不用于装包。
4. 本对话自带工具（`AGENT` = `cursor` 时是 Read / Write / Grep / Glob / Shell，`dsh` 时是 read / write / grep / glob / pwsh）和 PowerShell 内建始终可用。不要用 Shell 反复 which。
5. `commit` / `push`：当天 `commands` 含 `git`，且用户明确要求，并遵守用户 git 规则。

### 仓对齐

仅本轮要对技能仓做 git（fetch / pull / push / commit，或用户说同步 skill）时做。开场不做。完成：走完下面一条路径，或失败已报告。

`<skill根目录>` = 加载本文件时给出的目录，不写死盘符。

1. `git -C "<skill根目录>" status -sb`：首行 `## 分支...上游 [ahead N, behind M]`，其后每行一个改动文件。
   - 报错（没有 git 或不在仓库里）→ 跳过，用本地继续。
   - 有改动文件行 → 报 dirty，结束。脏树不 pull、不 commit。
   - 首行无 `...上游` → 报无上游，结束。
2. `git -C "<skill根目录>" fetch`：失败或超时 → 报「fetch 不通，用本地继续」，结束。不重试、不 pull。
3. 再 `git -C "<skill根目录>" status -sb`，只看首行的 ahead（左）/ behind（右）：

| ahead / behind | 动作 |
|---|---|
| `behind>0`、`ahead=0` | `git pull --ff-only`；失败则报告，结束 |
| `ahead>0`、`behind=0` | 问用户是否 push，等确切回复。本步不 commit、不 push |
| 两者都>0 | 报分叉，结束 |
| 都为 0 | 不说话，继续本轮任务 |

`status -sb` 的 ahead/behind 是相对上次 fetch 的值，所以第 3 步必须读 fetch 之后的。

白名单例外：本流程的 `status` / `fetch` / `pull --ff-only` 不先读环境卡；`commit` / `push` 仍须当天 `commands` 含 `git`、用户明确要求，并遵守用户 git 规则。只用快进，分叉只报告。

### 命令行列目录

要找文件或看某目录里有什么时：先选工具，选中一种就做完。

#### DSH（`AGENT` = `dsh`）

1. 找文件名 → `glob`：`path` 给最小父目录，pattern 收窄（`src/**/*.ts`）。
2. 找内容 → `grep`。
3. 要清单 / 媒体 / 二进制 / 刚落盘的文件 → `Get-ChildItem -LiteralPath <父目录>`。
4. 结果里出现 spill 路径时 → `read` 或 `grep` 那个文件取全量。
5. 每条命令前先 `[Console]::OutputEncoding=[Text.Encoding]::UTF8`。

#### Cursor（其余 `AGENT`）

Glob：工作区里按模式找源码和文本（`.py` `.md` `.ts` 等）。走索引，通常比扫盘快。父目录已知则把范围限定在那里。

列目录：已知父目录要清单；找媒体或二进制（视频、音频、图片、压缩包）；或要刚落盘、索引可能还没有的磁盘实况。索引默认不含这类文件。步骤：

1. 用本对话的 PowerShell，不用 cmd。
2. 把控制台输出设成 UTF-8。
3. `Get-ChildItem -LiteralPath <父目录>`。名字含非 ASCII 时用 `-LiteralPath`，或 `-Filter` 之后取 `.FullName`。
4. 读文件内容用 Read。

---

## 4. 输出要求

用户给了明确任务：直接出任务结果。

只是招呼语或无目的闲聊：在输出中包含四行运行结论，不带判据。

```html
- **AGENT** = `<dsh | cursor | codex | 其它>`
- **系统** = `<Windows | Linux | macOS>`
- **工作目录** = `<路径>`
- **命令** = `<逐条抄 catalog 里各 skill description 末尾的 命令：/xxx，空格分隔，一行>`
```

命令只抄 catalog 里现成的 description，不另写清单、不补 catalog 里没有的。用户触发 skill 不在 catalog 里，走 `/` 菜单，不列。
