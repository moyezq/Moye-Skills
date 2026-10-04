---
name: self-session-bootstrap
description: 新对话第一条用户消息必须先读本 skill——开场硬前置，全局约束与开场规矩都在这里。本对话尚未读过它、或用户说「先读规范 / 先看 skills」时同样先读。读时判当前 Coding Agent；系统命令日探测用到才做。
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
- 默认编程语言 Python。
- 可独立完成的简单、确定多步活优先派 SubAgent；一眼能查的用本对话工具，不派。主问题仍在本对话做。
- 验证由用户手动执行；AI 只做静态审查和逻辑说明。默认不跑 `test_*.py`、`.sh`、`.bat` 及业务入口脚本；用户本轮明确要求「跑通再写入文档 / 验证真实可用」时 → 跑用户点名的那个。
- 任务结束后不主动新建说明用 `.md`。用户明确要求、或更新与任务相关的 README / docstring / 阶段注释除外。
- 删模块、改配置路径、换入口后，在回复中请用户重启服务再手动验证；勿把仍在跑的旧进程当成新代码已通过。
- Agent 为探测或联调起服务（HTTP、向量、Vite）→ 测完立刻停掉，不常驻占端口；用户终端里已在跑的进程不要杀。
- `AGENT` = `dsh` 时改文件先读：`edit` / `write` 前对目标路径调一次 `read`。
  - 批量改多个文件 → 先并行 `read` 全部目标再动手。
  - 目标只用 `grep` / `glob` / `pwsh` 看过 → 照样 `read`。
  - 会话恢复或 fork 过 → 重读。
  - 派 SubAgent 改 → 子 agent 自己 `read`。
  - 改名 / 移动 / 重构目录后（`Move-Item`、`git mv`）→ 新路径先 `read` 再 `edit`。
  - 能先改后移的 → move 放最后。
- `edit` 的 `old_string` 从**刚读到的输出里复制**。凭记忆重写会因为缩进、被省略的行、错字而失配，白费一整轮。
- **同一文件的改动一次改完**：先把要改的几处读齐，再发一次 `edit`（或一次 `write`）。步数是成本的量级杠杆——
  缓存读取总量 ≈ Σ(每步的上下文)，而上下文单调增长，所以总花费近似随步数**平方**增长；同一个文件连发四次小改，四次都重读同一份上下文。
- **反复要用的检查落进仓里**：回归比对、指纹、结构扫描这类第二轮就写成仓内的一份测试或脚本，用仓内的固定落点，
  别每轮现写一个临时文件。落点见本仓 `AGENTS.md`（系统 Temp 在沙箱下常被拒写）。

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

### Git操作

当涉及 Git 操作（fetch / pull / push / commit，或用户说同步 skill）时，读同目录 [agent-git-op.md](./agent-git-op.md)，按它执行。开场不读。

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

**报成果按固定形状**：能力 → 触发场景 → 指标（前 → 后）→ 靠什么验证。能用数字就用数字（格式数、页 / 列 / 张 / 条数、调用或落盘次数、耗时、成本、字段数）；**没有数字的形容一律不写**（「重构了 X」「优化了 Y 模块」「完善了机制」）；给不出指标的改动（纯文档、纯重命名）直说「这次没有能力或指标变化」；没有性能改动就不写性能。

**给用户的跑法必须可观测**：凡让用户执行命令或操作，同时给三件事——怎么看出问题、失败在哪一步、耗时在哪。别把长等待（例如几十条用例各等一次超时）与满屏噪音留给用户。

招呼语或无目的闲聊 → 输出运行结论，不带判据：

```html
- **AGENT** = `<dsh | cursor | codex | 其它>`
- **系统** = `<Windows | Linux | macOS>`
- **工作目录** = `<路径>`
- **命令**（catalog 里 description 带 `命令：` 尾巴的 skill，照抄、按 catalog 顺序列全）
  - `/xxx` —— 该 skill 的一句话作用
```
