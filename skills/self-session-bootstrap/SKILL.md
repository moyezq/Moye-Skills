---
name: self-session-bootstrap
description: 新对话第一条用户消息必须先读本 skill——开场硬前置，全局约束与开场规矩都在这里。本对话尚未读过它、或用户说「先读规范 / 先看 skills」时同样先读。读时判当前 Coding Agent。
---

# 会话索引

本文件不是某个具体任务的写法。三块：§1 开场一次，§2 全程约束，§3 输出要求。读完按用户这一轮的任务继续；不要向用户复述本文件全文，除非对方在问规范本身。

先读仓库根 `.env`，拿到本机专属环境变量（`MOYE_SKILLS_ROOT`、`WORKSPACE_ROOT`、`NOTES_ROOT`、`NPM_CACHE`）；skill 正文不写死盘符与用户名，要用绝对路径就取这里的键。

---

## 1. 开场

本对话只做一次，按序：

1. 读完本文件。

2. 通过已注入的系统提示词，判断当前 Coding Agent（`dsh` / `cursor` / `codex` / 其它），记作 `AGENT`。

3. 判当前系统：看命令工具跑的是哪种 shell——PowerShell（`dsh` 的 `pwsh`、`codex` 的 `exec_command`、`cursor` 的 `Shell`）→ Windows；`bash` → Linux / macOS。硬确认按 shell 分支：PowerShell Core 跑 `$IsWindows`；**Windows PowerShell 5.1（cursor 默认）没有 `$IsWindows`**，跑 `$PSVersionTable.PSEdition`（`Desktop`）或 `[Environment]::OSVersion`；Linux / macOS 跑 `uname -s`（Linux / Darwin）。

4. 认出**本 skill 自己的目录**（下称 `<skill根目录>`；各 skill 正文里的这个占位都指这一层，就是加载时给本文件的那一层）：

   - `dsh` 看加载时给的「Base directory for this skill」那行。
   - `cursor` 看 `available_skills` 里本文件 fullPath 的父目录。
   - `codex` 看清单条目尾部的 `(file: r0/<名字>/SKILL.md)`，再用注入的全局 `Skill roots` 表把 `r0` 解析成真实路径（`r1`–`r6` 是 codex 自带的系统与插件 skill，不是本仓）。

   别把它和**工作树**搞混：`%USERPROFILE%\.dsh\skills`、`%USERPROFILE%\.cursor\skills`、`%USERPROFILE%\.agents\skills` 都只是指向同一个工作树的目录联接，由本仓 `setup.ps1` 按根目录 `.env` 建立；`<skill根目录>` 是工作树下面**单个 skill** 的那一层。skill 只有这一份正文，读与写都落在 `<skill根目录>`。命令与路径随系统走，不写死盘符。

5. **系统命令白名单**：读环境卡 `<skill根目录>/scripts/_meta/env_card.json` 的 `commands`；`commands_date` 不是今天就跑一次只读探测，拿到当天必定可用的第三方命令清单：

   ```powershell
   python -c "import sys; sys.path.insert(0, r'<skill根目录>/scripts'); import env_detect; print(env_detect.list_available_commands())"
   ```

   不在清单里的命令不用，也不罗列缺什么。要增删探测项只改 `env_detect.py` 顶部的 `COMMANDS_TO_CHECK`；这不是为任务跑 Python。

6. **Conda 环境**：读环境卡同一份的 `conda_envs`；`conda_date` 不是今天就跑一次只读探测，拿到本机环境名清单：

   ```powershell
   python -c "import sys; sys.path.insert(0, r'<skill根目录>/scripts'); import conda_envs; print(conda_envs.list_conda_env_names())"
   ```

   默认环境 `base`；项目 README 或用户点名了才换（如 `rag`）。不要跑 `pip list`。

7. **Harness 操作**：按第 2 步的 `AGENT`，读 `<skill根目录>` 下对应的一份，按它执行，别读别家那份：

   - `dsh` → `<skill根目录>/agent-dsh.md`
   - `cursor` → `<skill根目录>/agent-cursor.md`
   - `codex` → `<skill根目录>/agent-codex.md`
   - 其它 → 不读，按该 harness 自带工具照通用做法做。

   每份同一套六块：读文件与列目录 / 改文件 / 运行 Python 脚本 / Git 操作 / 权限与提权 / 长跑、后台与服务。

   三端共用的三条先照这个：新建文件直接写；改已有文件先读再改；一个文件要改多处就一次改完，生成文件（`.d.ts`、绑定的模型声明、前端产物）不手改、改源头再重跑。

开场只做这七步。其它正文：用到才读，读过不重读。

---

## 2. 全程约束

只放跨任务、且没有更专门 skill 承接的规则。

- 用中文回答。
- 默认编程语言 Python。
- 可独立完成的简单、确定多步活优先派 SubAgent；一眼能查的用本对话工具，不派。主问题仍在本对话做。
- 验证由用户手动执行；AI 只做静态审查和逻辑说明。默认不跑 `test_*.py`、`.sh`、`.bat` 及业务入口脚本；用户本轮明确要求「跑通再写入文档 / 验证真实可用」时 → 跑用户点名的那个。
- 任务结束后不主动新建说明用 `.md`。用户明确要求、或更新与任务相关的 README / docstring / 阶段注释除外。
- Agent 为探测或联调起服务（HTTP、向量、Vite）→ 测完立刻停掉，不常驻占端口；用户终端里已在跑的进程不要杀。

- **先跑一次真实入口，别先推理数据流**：现象与真因常常不在代码表面上，程序自己说出来的错误比分段重构便宜得多。跑不动或太贵时，退一步打一次真实输出或错误；拿到事实再只读被点名的那一层。排障时先看清报障要的是哪个量，再谈修好没有；构建通过不等于报障点验过。
- 删模块、改配置路径、换入口后，在回复中请用户重启服务再手动验证；勿把仍在跑的旧进程当成新代码已通过。
- 写文件前先读要改的那个文件（具体做法见 §1 第 7 步对应的那份 harness 文档）。

---

## 3. 输出要求

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
