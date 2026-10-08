# Moye-Skills

个人 skill 仓库。clone 后把各产品的个人 skills 目录联接到本仓 `skills/`，不要再各拷一份。

本机路径写在 `.env`，不要写进 README。

## clone 与装

```powershell
git clone git@github.com:moye233057/Moye-Skills.git
cd Moye-Skills
copy .env.example .env
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

`setup.ps1` 读仓库根 `.env`，把三个产品的个人 skills 目录做成指向本仓 `skills/` 的**目录联接**。联接做完重启 Cursor / dsh 才认。第一次跑时若没有 `.env`，脚本会从 `.env.example` 复制一份并停下，等你填完再跑一次。

## `.env` 要填什么

`.env` **不进仓**（已在 `.gitignore`），模板是 [.env.example](.env.example)。两类值：

| 键 | 填什么 | 谁用 |
|---|---|---|
| `CURSOR_SKILLS` / `DSH_SKILLS` / `CODEX_SKILLS` | 三个产品扫个人 skills 的目录，模板里给的是 `%USERPROFILE%` 展开后的默认位置 | `setup.ps1` |
| `PREINSTALL_SKILLS` | 取源脚本落上游 skill 的暂存目录（相对本仓根，缺省 `preinstall`） | `self-skill-crud` |
| `GITHUB_PAT` | 可选。fine-grained PAT，权限 `Contents: Read and write`；留空则拉取与推送交你自己的终端 | `agent-dsh.md` 的 Git 一节 |
| `MOYE_SKILLS_ROOT` | 本仓绝对路径；skill 目录 = `%MOYE_SKILLS_ROOT%\skills\<名字>` | 需绝对路径的 skill |
| `WORKSPACE_ROOT` | 工作区根（本仓所在的那一级目录） | 需绝对路径的 skill |
| `NOTES_ROOT` | 知识库 `笔记库` 的根 | `self-notes-read` |
| `NPM_CACHE` | `npx` 缓存目录。**写全路径**：读取方只展开 `%VAR%` 这类系统变量，不认同一个 `.env` 里的另一个键 | `self-skill-crud` |

值里可以写 `%USERPROFILE%` 这类系统环境变量，读取方会展开。skill 正文不写死盘符与用户名——要用绝对路径就从这里的键取；哪个 skill 用哪个键写在该 skill 自己的正文里。

## 日常用

- **会话**：新对话开场读 `self-session-bootstrap`，它决定这一轮按哪套工具干活；命令从对话里的 skill 目录现抄，本文件不维护清单。
- **加 / 改 / 删 skill**：走 `self-skill-crud`（流程在它的 `references/`）。删 skill 时连带改 `skills-list.md` 与 [`CONTEXT.md`](CONTEXT.md)。
- **清单与术语**：[`skills-list.md`](skills-list.md) 是给人看的薄索引，[`CONTEXT.md`](CONTEXT.md) 是本系统特有叫法的术语表，决策与废弃理由在 [`docs/adr.md`](docs/adr.md) / [`docs/HISTORY.md`](docs/HISTORY.md)。

## 验收

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
git remote -v
```

`setup.ps1` 对已经指向本仓 `skills/` 的联接会打印 `ok`；报别的就说明那一条联接指到了别处（常见是指到另一个产品的 skills 目录）。`origin` 用 SSH。

## 不要放进仓

`.env`（含密钥、本机路径）、`preinstall/`（还没审过的上游第三方代码）、`*-workspace/`（试验与探查的过程文件）、`.idea/`（IDE 本地状态）。都在 `.gitignore` 里。
