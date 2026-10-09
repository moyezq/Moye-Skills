# cursor 操作规范

会话索引 §1 第 7 步按 `AGENT` 读本文件：`AGENT` = `cursor` 时读这一份，别读另外两份。以下为 2026-10-08 Cursor 会话实测（原始输出见 `docs/agent-cursor-verify.md`）。

工具集：`Read` / `Write` / `StrReplace` / `Grep` / `Glob` / `Shell`，另有 `Delete`、`AwaitShell`。**定点替换的工具叫 `StrReplace`，本机没有名为 `Edit` 的工具。**

## 1. 读文件与列目录

- `Glob`：工作区里按模式找源码和文本（`.py` `.md` `.ts` 等）。走索引，通常比扫盘快；父目录已知就把范围限定在那里。
- `Grep`：找内容。
- `Read`：读文件内容。
- 列目录：已知父目录要清单；找媒体或二进制（视频、音频、图片、压缩包）；或要刚落盘、索引可能还没有的磁盘实况（索引默认不含这类文件）。用本对话的 PowerShell，不用 cmd：

  1. 把控制台输出设成 UTF-8。
  2. `Get-ChildItem -LiteralPath <父目录>`。名字含非 ASCII 时用 `-LiteralPath`，或 `-Filter` 之后取 `.FullName`。

- 不要用 Shell 反复 which 探命令；要知道有哪些命令，见会话索引 §1 第 5 步。

## 2. 改文件

- `StrReplace` 做定点替换，`Write` 做整份替换，删文件用 `Delete`。
- 先读后改、一次改完；本机未测出与 dsh 的差异。

## 3. 运行 Python 脚本

**`conda activate` 在 Cursor 的 PowerShell 里有效**：实测 `conda activate rag` 后 `python` 落到 `<conda 根>\envs\rag\python.exe`，`conda deactivate` 回 base。而且 **Shell 跨调用保留状态**——上一轮 activate 过的环境会带到下一轮，除非显式 `deactivate` 或换掉。

- 所以默认写 `conda activate <环境>` 再 `python`；要确定性时用显式路径 `<envs>\<环境>\python.exe`（base 是 `<conda根>\python.exe`）。
- 拿不准当前哪个环境时先 `python -c "import sys;print(sys.executable)"`，别看变量。
- 输出有中文先设 `$env:PYTHONUTF8='1'`。

## 4. Git 操作

- 本地与远端都照跑：`fetch` / `pull --ff-only` / `push` 不加 `-c`、不改写 URL、不读 `GITHUB_PAT`。
- **不要走 dsh 那条 PAT `insteadOf`**：本机实测 Cursor 会话里会 `Connection was reset` 或挂死。
- 同步本地→远程：普通 `add` / `commit` / `push`。`push` 失败再交用户终端。
- **状态分派（三端共用）**：`git -C "<仓根>" status -sb` 首行是 `## 分支...上游 [ahead N, behind M]`，其后每行一个改动文件。没有 git / 不在仓库里 → 跳过用本地继续；有改动文件行 → 报 dirty 不结束（dirty 只挡 `pull`）；首行无上游 → 报无上游结束。`ahead>0` → 报领先并问是否 push；`behind>0` 且干净 → `pull --ff-only`；两者都>0 → 报分叉结束；都为 0 → 不说话。用户说「同步」＝授权 `commit` 一条并 `push`；没听到就只问。
- `<仓根>` = `skills/` 的上一级（有 `.git` 的那层）。
- `commit` / `push` 仅用户明确要求时做，禁止 force，分叉只报告。要验证远端写路径时，只在 `probe/<时间戳>` 临时分支上做（`push --dry-run` 零副作用；真写就去掉 `--dry-run`，写完立刻 `push origin --delete probe/<时间戳>`）；不碰 `main`、不 force、不改 remote 配置。

## 5. 权限与提权

本机 Cursor 会话默认偏宽松：`Out-File` 写 `%LOCALAPPDATA%\Temp`，以及 `Write` 工具写同一处，**都成功**，未观察到拒绝。

- 先正常做；**真遇到拒绝**时对**同一条命令**申请一次权限重试，仍被拒就报告并停。
- 「写工作区外会被拦」在本机 Cursor 上证据不足，不要当硬规则背。

## 6. 长跑、后台与服务

已实测：起一个 `127.0.0.1` 的临时 HTTP 服务 → 探到 200 → 立刻 `shutdown` 停掉。

- 起服务（HTTP、向量、Vite）→ 验端口 → 测完立刻停，不常驻占端口。
- 用户终端里已在跑的进程不要杀；动手前先认身份（`Get-Process` 看 `Path` 与 `StartTime`，`netstat -ano` 看端口归属）。
