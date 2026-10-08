# dsh 操作规范

会话索引 §1 第 7 步按 `AGENT` 读本文件：`AGENT` = `dsh` 时读这一份，别读另外两份。以下都是本机实测过的做法。

工具集：`read` / `write` / `edit` / `grep` / `glob` / `pwsh`。PowerShell 内建始终可用。

## 1. 读文件与列目录

- 找文件名 → `glob`：`path` 给最小父目录，pattern 收窄（`src/**/*.ts`）。
- 找内容 → `grep`；要看上下文再 `read` 命中文件。
- 读文件 → `read`，长文件用 `offset` / `limit` 接着读。
- 要清单 / 媒体 / 二进制 / 刚落盘的文件 → `Get-ChildItem -LiteralPath <父目录>`。
- 工具输出被截断时会给出一个 spill 路径 → 用 `read` 或 `grep` 那个文件取全量。
- 每条 `pwsh` 命令前先 `[Console]::OutputEncoding=[Text.Encoding]::UTF8`（管控制台回显）。子进程 python 的中文输出**不归它管**——只设它、不设 §3 的 `$env:PYTHONUTF8='1'`，落盘与回显照旧乱码。
- 不要用 Shell 反复 which 探命令；要知道有哪些命令，见会话索引 §1 第 5 步。

## 2. 改文件

- 改已有文件：先 `read`，`old_string` 从刚读到的输出里**原样复制**。凭记忆重写会因缩进、省略行、错字而失配。
- 一个文件要改多处：一次 `edit` 改完，不发多次小改。`old_string` 必须唯一，多处相同时带上下文或 `replace_all`。
- 只有新建或整份替换才用 `write`。
- **生成文件不手改**：`.d.ts`、绑定的模型声明、前端产物这类由构建或生成命令写出的文件，手改下一次生成就被覆盖。要变就改生成它的源头，再重跑那条命令；跑完这些文件都变了，接着改先重读。
- 写工具会拒三种：`old_string` 失配、`old_string` 命中多次、`file changed since it was read`（别人刚写过）。**撞到任何一种就重读一次再改，不要靠重试。**

## 3. 运行 Python 脚本

- 解释器用 `python`（PATH 上就是 base），某个环境用 `<envs>\<环境>\python.exe`。**`conda activate` 在非交互 shell 里静默无效**：不报错、`CONDA_DEFAULT_ENV` 为空、`python` 落到 base。
- 输出有中文先设 `$env:PYTHONUTF8='1'`，否则重定向落盘是 GBK，读回来是乱码。
- 命令的 stdout 会被工具截断，长输出按第 1 条取 spill 文件。
- 非交互 shell 里 stdin 类提问**立刻 `EOFError`**（实测 `input()` 0.1s），不用为它设防；读控制台的凭据提示是另一回事，见 §4。
- 起带空格参数的外部命令**别用 `Start-Process -ArgumentList`**（它按空格切开）：`-c 'import conf; print(1)'` 到了解释器只剩 `import`，报 `SyntaxError` 却看着像跑过了（实测 9 条探针全是假 ok）——直接 `& <解释器> -c "…"`，或把代码落成 `.py` 再跑。
- 量"有没有卡住"用 `$p.WaitForExit(<毫秒>)`（返回 bool）再看 `$p.ExitCode`；`Wait-Process -Timeout` 出错会静默返回、`$p.HasExited` 仍是 `$false`，把刚起 0.1s 的进程误报成 HUNG（实测 6 条假 HUNG）。

## 4. Git 操作

**本地**：`status` / `log` / `diff` / `add` / `commit` 照跑。

**远端**：`<仓根>` 指**仓库根**（`.git` 与 `.env` 都在那一层，不是 `skills/`）。默认走下面这条 PAT 形式：`-c credential.helper=` 去掉凭据助手，`-c $instead` 把 SSH 地址改写成 HTTPS。凭据助手或交互口令一介入就可能**挂死到超时**，所以不重试、不等待。（2026-10-08 复查：本机 SSH 免密可通时 `ls-remote` 5.9 秒就返回，「必挂死」不成立；按这条形式走仍然是对的。）`$pat` 读自 `<仓根>/.env` 的 `GITHUB_PAT`（不打印、不外传）：

```powershell
$instead = "url.https://x-access-token:$pat@github.com/.insteadOf=git@github.com:"
git -C "<仓根>" -c credential.helper= -c $instead <fetch|pull --ff-only|push>
```

`GITHUB_PAT` 缺失、失效，或写被远端拒绝时，把 `git push` 交给用户在**自己的终端**跑；同一轮报文件清单与 message。`-c $instead` 会把 token 拼进 URL——任何输出落进文档或发给用户前先 `-replace` 洗掉。

**状态分派（三端共用）**：`git -C "<仓根>" status -sb` 首行是 `## 分支...上游 [ahead N, behind M]`，其后每行一个改动文件。没有 git / 不在仓库里 → 跳过用本地继续；有改动文件行 → 报 dirty 不结束（dirty 只挡 `pull`）；首行无上游 → 报无上游结束。`ahead>0` → 报领先并问是否 push；`behind>0` 且干净 → `pull --ff-only`；两者都>0 → 报分叉结束；都为 0 → 不说话。用户说「同步」＝授权 `commit` 一条并 `push`；没听到就只问。

`commit` / `push` 仅用户明确要求时做，禁止 force，分叉只报告。要验证远端写路径（例如怀疑凭据或远端配置）时，只在 `probe/<时间戳>` 临时分支上做：`push --dry-run origin main:refs/heads/probe/<时间戳>` 零副作用；真要写就去掉 `--dry-run`，写完立刻 `push origin --delete probe/<时间戳>`。不碰 `main`、不 force、不改 remote 配置。

## 5. 权限与提权

三种文件策略：`read-only` / `workspace-write` / `danger-full-access`。`workspace-write` 下，子进程（`pwsh` 里跑的 python / git）能不能写，看路径落在哪一列：

| 路径 | 子进程 | `write` / `edit` 工具 |
|---|---|---|
| 工作区根，以及本次会话新建的目录 | 可写 | 可写 |
| **会话开始前就存在的子目录**（仓库树本身，含 `.git/`） | **被拒** | 可写 |
| 工作区外（conda 环境目录、用户目录） | **被拒** | — |

要落盘的活先看输出目录在哪一列：入库写 `data/`、`pytest` 写缓存、`git commit` 写 `.git/` 都落在第二列 → 切**完全权限**，或交用户终端。读取与 `write` / `edit` 工具不受这一列限制。（2026-10-08 实测：一个仓里 `.git/`、`skills/`、某个别的项目的 `tests/` 三个子树全被拒，工作区根可写可删；`pytest` 跑完仓里一个新 `.pyc` 都没有。）

- 被拒的报错有两种写法——裸 `Access to the path … is denied`，或带 `[sandbox: file access denied under …]`：**按路径判自己在哪一列，不要按报错文案判，也不要去修文件权限**（两者都与 DACL、只读位、完整性标签无关，补完全控制不改变现象）。
- `pip install` 写 conda 环境目录落在第三列。
- **例外一（起局错）**：沙箱**给自己授不上写权**时报 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(<路径>)`，连工作区根都写不了，症状是**裸 `Access denied`**、不带策略标记。**重试无用**——要起受限子会话，工作区放 `%TEMP%` 之类，别放仓内子树。
- **例外二**：目录缺 `WRITE_OWNER` 时授权也落不下去；这一种才轮到修文件权限，但同一会话内补完不保证立刻生效（授权是起局时落的）。
- 被拒时的两条路：把那条命令交给用户终端，或对**同一条命令**提权一次（一次一个批准）。
- 批准提示关闭时会话里，提权请求会被直接拒；这时只走用户终端，不反复申请。工具输出里可能同时出现 `[sandbox: escalation available — retry this exact command once with sandbox_permissions …]`，别被它带着反复申请。

**另一类被拒：目录的 mode**（不在三种策略里，也不是文件权限）

- 环境：受限子进程（`read-only` / `workspace-write`）；完全权限下没有这个问题
- 场景：脚本要个落盘目录；用例要用 `tmp_path` / `tmpdir` / `tmp_path_factory`——报错栈落在 `_pytest/pathlib.py` 的 `os.scandir` 就是这一条
- 操作：不用带 mode 的建法（`os.mkdir(p, 0o700)`、`tempfile.mkdtemp()`、`TemporaryDirectory()`、`tmp_path` 系）——它们建的目录创建者自己列不出、写不进、也删不掉（`WinError 5` / `EACCES`；补权限、修 ACL 都不解决）
- 步骤：`(Path(tempfile.gettempdir()) / "<名字>").mkdir()`；pytest 里换成项目已有的目录夹具，没有就按这一行补一个；整仓测试都要 `tmp_path` 又没有这种夹具时，切完全权限跑

## 6. 长跑、后台与服务

**没有一条活可以在没有上限、没有进度的情况下跑**——跑一小时的静默任务等于卡死，而且没人会发现。

- 上限：每个等待都自带上限（连接、读、子进程、重试次数），熔断只是全都失效时的兜底——脚本见 `self-python-script`「运行上限」（默认 5 分钟，更久先问，拉起的子进程也要收）；测试见 `self-python-testing`「pytest.ini 第一版就带熔断」；前台调用 `timeoutMs` ≤ 120000。
- 进度：每批 / 每阶段打一行并 `flush=True`；一行不出的长活按卡死处理。
- 追踪：分钟级任务用 `run_in_background` 拿 job id，起完去干别的、完成会通知，不要 busy-poll、不重复起同一个 job。前台只跑秒到分钟级的活——前台的活只有「超时转后台」这一层保险，提前中止就什么都没有：没有 job id、没有通知、进程还活着。
- 收尾前用 `job_output` 收未读结果、`job_kill` 停掉不再需要的 job，不留后台任务。
- **停作业与中止一轮都只杀 pwsh 外壳，孙进程会活下来**（兜底）：`job_list` 显示 killed 而端口仍被占；被中止的 `pytest tests -q` 曾成孤儿、自旋一小时烧 3400s CPU，而同一命令正常 21s。每次停 job 或中止一轮后查一遍：`Get-Process python -ErrorAction SilentlyContinue | Select-Object Id,StartTime,CPU,Path`。
- 收孤儿用 `Stop-Process -Force` 或 `psutil`；**别用 `taskkill`**——受限沙箱里实测 `ERROR: Access denied`，连自己刚起的子进程都杀不掉。
- 按命令行模糊匹配杀进程会**连自己一起杀**：匹配串出现在你自己（或 pwsh）的命令行里时，先杀的就是自己（实测 exit 15、半轮探针白跑）。按 pid 精确杀；非要模糊匹配就把匹配串拼出来（`"dsh-probe-" + "marker"`），匹配时跳过自己与父进程的 pid。
- 起服务（HTTP、向量、Vite）：起 → 验端口 → 测完立刻停，不常驻占端口。用户终端里已在跑的不要杀。
- 杀进程前先认身份：`Get-Process` 看 `Path` 与 `StartTime`，`netstat -ano` 看监听端口的 PID，确认是自己的孤儿再杀。跨会话的进程在受限子进程里**可能列不出来**（实测别人会话起的 8030/8031 不在 `Get-Process` 里、在 `netstat -ano` 里）——列不出来时，监听端口的按 `netstat` 的 PID 判，别当成已退出。
