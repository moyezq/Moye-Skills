# Git 操作

会话索引 `self-session-bootstrap` 的 Git 分支。仅本轮涉及技能仓 git（fetch / pull / push / commit，或用户说同步 skill）时读，开场不读。

完成：走完下面一条路径，或失败已报告。

`<skill根目录>` = 会话索引 `SKILL.md` 所在目录（本文件同目录），不写死盘符。

## 远端命令怎么跑（按 AGENT）

`AGENT` = `dsh`（SSH 与凭据助手会挂死，须走 HTTPS PAT）：

- 能做：本地——`status` / `log` / `diff` / `add` / `commit`；远端只允许带下面两个 `-c` 的 `fetch` / `pull --ff-only` / `push`。
- 不能做：不带那两个 `-c` 的 `fetch` / `pull` / `push`——一律挂死到超时，不重试、不等待。
- `$pat` 读自 `.env` 的 `GITHUB_PAT`（不打印、不外传），然后：

  ```powershell
  $instead = "url.https://x-access-token:$pat@github.com/.insteadOf=git@github.com:"
  git -C "<skill根目录>" -c credential.helper= -c $instead <fetch|pull --ff-only|push>
  ```

  同步本地→远程：先 `add` / `commit`，再按上式 `push`。`GITHUB_PAT` 缺失或失效时，把 `git push` 交给用户在**自己的终端**跑；同一轮报文件清单与 message。

`AGENT` = `cursor`（本机实测：SSH 直通；HTTPS PAT insteadOf 会 reset / 挂死）：

- `fetch` / `pull --ff-only` / `push` **照跑**：不加那两个 `-c`、不改写 URL、不读 `GITHUB_PAT`。
- 不要走 dsh 那条 PAT `insteadOf`——Cursor 会话里会 `Connection was reset` 或挂死。
- 同步本地→远程：普通 `add` / `commit` / `push`。`push` 失败再交用户终端。

`AGENT` = `codex`（sandbox 默认无网络；走普通 SSH）：

- 读远端状态/同步：`git` 直接走现有 SSH remote，不加 dsh 那两个 `-c`、不改写 URL、不读 `GITHUB_PAT`。
- Codex sandbox 第一次连 `github.com:22` 可能报 `Permission denied` 或连接失败；这不是认证失败。把同一命令申请网络权限后重跑，仍走 SSH。
- 命令统一设 `GIT_TERMINAL_PROMPT=0`，SSH 用 `BatchMode=yes` 和 `ConnectTimeout=10`，避免等待交互口令；口令/密钥不可用时交用户终端，不自动切 PAT。

  ```powershell
  $env:GIT_TERMINAL_PROMPT = '0'
  git -C "<skill根目录>" -c core.sshCommand="ssh -o BatchMode=yes -o ConnectTimeout=10" <fetch|pull --ff-only|push>
  ```

- `push` 仍按共用分派：仅用户明确要求，禁止 force；分叉只报告。

**Codex 操作分流（本地 / 插件 / SSH）**：

工具名形如 `mcp__codex_apps__github._fetch_file`；下表用短名。插件走 Codex 后端，不依赖本机外网；当前会话已实测通。

| 场景 | 首选 | 最简步骤 |
|---|---|---|
| 本地工作树已有内容 | 本地工具 | 直接 `Read` / `git status -sb`；不要调 `fetch_file` |
| 远端文件、分支、commit | GitHub 插件 | `fetch_file`（带 `path` / `ref` / `start_line` / `end_line`）；分支 `search_branches`；历史 `search_commits` |
| Issue / PR | GitHub 插件 | `search_issues` / `search_prs` → 命中后 `fetch_pr` / `fetch_pr_patch` |
| CI | GitHub 插件 | `get_commit_combined_status` → `fetch_commit_workflow_runs` → `fetch_workflow_run_jobs` → `fetch_workflow_job_logs` |
| 单文件远端写 | GitHub 插件 | `fetch_file` 取 `sha` → `create_branch` → `create_file` / `update_file` / `delete_file`；要 PR 再加 `create_pull_request`（未实测） |
| 临时分支清理 | SSH | `git push origin --delete <branch>`；插件没有 `delete_branch` |
| clone / fetch / pull --ff-only / push / 多文件提交 / 本地历史 | SSH | 走上文 SSH 命令；sandbox 网络失败就申请权限重跑 |
| 插件 transport / HTTP 失败 | 先插件重试 | 原样重试 1 次；仍失败：Git 类动作转 SSH，Issue / PR / CI / 远端写报告阻塞 |
| 未明确要求 | 禁止写 | 不调 `create_*` / `update_*` / `delete_*` / `merge_*` / 评论 / reaction |

已验证读：`get_repo`、`fetch_file`、`search_branches`、`search_commits`、`search_issues`、`search_prs`、`get_commit_combined_status`、`fetch_commit_workflow_runs`。已验证写：`create_branch`、`create_file`、`update_file`、`delete_file`（临时分支已清理）。未实测：`create_pull_request`、merge、评论 / reaction；仅在用户明确要求时使用。账号权限为 `admin`。写操作可能 1–2 分钟，调用中不要重复提交，失败后先读回核对。

其它 AGENT：与 `cursor` 相同。

## 状态分派（共用）

1. `git -C "<skill根目录>" status -sb`：首行 `## 分支...上游 [ahead N, behind M]`，其后每行一个改动文件。
   - 报错（没有 git 或不在仓库里）→ 跳过，用本地继续。
   - 有改动文件行 → 报 dirty 并列文件，但不因此结束：dirty 只挡 `pull`，不挡 `push`。
   - 首行无 `...上游` → 报无上游，结束。
2. 按首行分派。`ahead` 取本地读数。远端动作一律走上一节对应 AGENT 的跑法。

| 首行 | 动作 |
|---|---|
| `ahead>0` | 报「本地领先 N 条」，问是否 push；同意则按对应 AGENT 推（dsh 无 token 则交用户终端） |
| `behind>0`、`ahead=0`、工作区干净 | 按对应 AGENT 跑 `pull --ff-only`；失败则报告，结束 |
| 两者都>0 | 报分叉，结束 |
| 都为 0 | 不说话，继续本轮任务 |

用户说「同步」＝按对应 AGENT 的「同步本地→远程」；没听到「同步」就只按上表问。

白名单例外：本流程的 `status` / `pull --ff-only` 不先读环境卡；`commit` / `push` 仍须当天 `commands` 含 `git`、用户明确要求，并遵守用户 git 规则。只用快进，分叉只报告。
