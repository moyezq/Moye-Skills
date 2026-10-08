# codex 操作规范

会话索引 §1 第 7 步按 `AGENT` 读本文件：`AGENT` = `codex` 时读这一份，别读另外两份。以下由 Codex 在本机自测回填（2026-10-08），每条原始输出见 `docs/agent-codex-verify.md`（首轮确认清单与复检报告已合成那一份）。

工具集：`exec_command`（起 PowerShell 7.6.5 Core）。**没有** `read` / `edit` 这类独立文件工具。

## 1. 读文件与列目录

统一经 `exec_command` 在 PowerShell 内调 cmdlet：

- 读文件 → `Get-Content`
- 按模式找文件名 → `Get-ChildItem -Filter`
- 按内容找 → `Select-String`
- 列目录 → `Get-ChildItem`

## 2. 改文件

- 整份写入 → `Set-Content` / `Out-File`。
- 定点替换 → 自带 `apply_patch` 引擎，或 PowerShell 文本替换。
- 一个文件改多处：**一个** `apply_patch` 里写多个 `@@` hunk，已实测成功。
- 坑：从 PowerShell 直接调 `apply_patch.bat` 并传多行参数会失败（`Invalid patch: The last line of the patch must be '*** End Patch'`）。改调它底层那个 exe，**但那个路径要先展开**：`.bat` 里存的是 `%~dp0..\..\..\..\AppData\Local\OpenAI\Codex\bin\<hash>\codex.exe`，在 PowerShell 里原样调用会报 `The term '%~dp0…' is not recognized`。做法：读那个 `.bat`，把 `%~dp0` 换成**它所在目录**再拼出绝对路径，然后 `& <那个 exe> --codex-run-as-apply-patch`。

## 3. 运行 Python 脚本

经 `exec_command` 在 PowerShell 7.6.5 Core 里跑。其余同通用做法：用解释器路径（`python` 或 `<envs>\<环境>\python.exe`），输出有中文先设 `PYTHONUTF8=1`。

## 4. Git 操作

- 本地 `git commit` 可跑；本机当前要 `require_escalated` 才跑得动（原因见第 5 节）。
- `git push` 已验：本地 bare remote 全链路；真实网络的 SSH（`ls-remote` / `fetch` / `push --dry-run`）与一次真实 `probe/*` 分支写入 + 删除都通过。HTTPS 无凭据时快速失败，不挂住。
- `<仓根>` = `skills/` 的上一级（有 `.git` 的那层）。
- sandbox 默认无网络：第一次连 `github.com:22` 可能报 `Permission denied` 或连接失败，**这不是认证失败**。把同一命令申请网络权限后重跑，仍走 SSH。
- 命令统一设 `GIT_TERMINAL_PROMPT=0`，SSH 用 `BatchMode=yes` 与 `ConnectTimeout=10`，避免等待交互口令；口令 / 密钥不可用时交用户终端，不自动切 PAT。

  ```powershell
  $env:GIT_TERMINAL_PROMPT = '0'
  git -C "<仓根>" -c core.sshCommand="ssh -o BatchMode=yes -o ConnectTimeout=10" <fetch|pull --ff-only|push>
  ```

- **状态分派（三端共用）**：`git -C "<仓根>" status -sb` 首行是 `## 分支...上游 [ahead N, behind M]`，其后每行一个改动文件。没有 git / 不在仓库里 → 跳过用本地继续；有改动文件行 → 报 dirty 不结束（dirty 只挡 `pull`）；首行无上游 → 报无上游结束。`ahead>0` → 报领先并问是否 push；`behind>0` 且干净 → `pull --ff-only`；两者都>0 → 报分叉结束；都为 0 → 不说话。用户说「同步」＝授权 `commit` 一条并 `push`；没听到就只问。
- `commit` / `push` 仅用户明确要求时做，禁止 force，分叉只报告。
- **要验证远端写路径**（例如怀疑凭据或远端配置）→ 只在 `probe/<时间戳>` 临时分支上做：`push --dry-run origin main:refs/heads/probe/<时间戳>` 零副作用（连得上、认证过、协商完，但不更新 ref）；真要写就去掉 `--dry-run`，写完立刻 `push origin --delete probe/<时间戳>`。不碰 `main`、不 force、不改 remote 配置。

## 5. 权限与提权

- 默认策略 `workspace-write`；可写根包括工作区、本会话的 codex `visualizations` 目录、临时目录。
- 提权：对**同一条命令**传 `sandbox_permissions: "require_escalated"` 并给 `justification`；批准后命令在沙箱外运行（实测可写工作区外的路径）。
- **本机当前默认执行器故障**：启动命令前即报 `helper_unknown_error: setup refresh had errors`，连工作区内的命令也失败，只能走提权。故障解除前不要把「命令失败」当代码问题。

## 6. 长跑、后台与服务

短时 HTTP 服务已实测（起 → 验端口 → 立刻停，70 秒）。做法：起服务测完立刻停，不常驻占端口；用户终端里已在跑的进程不要杀。守护进程、多服务编排、故障恢复没验过——真到那一步再补。
