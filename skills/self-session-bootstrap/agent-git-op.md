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
