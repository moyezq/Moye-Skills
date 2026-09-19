---
name: find-skills
description: 从 skills.sh trending 榜发现可借鉴的远程 skill。人打 `/find-skills` 或 `/find-skills <关键词>` 才跑：只看榜前 20，每条都介绍它干什么；词表只用来标更贴近本机栈、优先深评并进。
disable-model-invocation: true
---

# Find Skills

完成标准：人打了 `/find-skills` 才跑；已取出 trending 前 20 个不重复 id；**每一条**（含未命中词表的、含 `seen` 沿用的）都有一句「它干什么」+ 一条结论；深评过的原文已落盘；简报已写进 `<工作目录>\skills-docs\find-skills\`；同一天覆盖时 `seen` 条目仍带着当日已写过的用途；`log.json` 已更新（含累计 `seen`）。本机 skill 正文未改（除非用户本轮已说「改文件」）。没有斜杠命令则不动。

目的是**发现**热榜上可能有用的 skill，不是只收关键词命中的。未命中词表仍要介绍用途，再决定并进 / 新建 / 笔记 / 放下。

## 触发

| 命令 | 怎么跑 |
|------|--------|
| `/find-skills` | 榜前 20 全部介绍；词表命中的优先按同栈做并进深评 |
| `/find-skills <关键词>` | 仍取榜前 20 并全部介绍；深评时把命中该词的放前面。词不在表内则当次停并说明 |

词表：`python` → `agent` → `react` → `爬虫` → `stars` → `fastapi` → `playwright` → `typescript` → `vite` → `debugging`。

`爬虫` 还匹配 `crawler` / `scrape` / `spider`。日志里仍记 `爬虫`。命中规则：`name` / `source` / slug 子串（大小写不敏感）。不要因为「skill 都是给 agent 用的」就算命中 `agent`。

## 日志

`log.json` 与本文件同目录。字段：

| 字段 | 含义 |
|------|------|
| `date` | YYYY-MM-DD，本地日历日 |
| `mode` | `trending` 或 `trending-keyword` |
| `keywords` | 本次用来标「贴近本机栈」的词 |
| `board` | 本次榜前 20：`[{id, name, source, installs, url}]` |
| `picked` | 已落盘原文的，按命中的词分组；未命中的放 `"_"` |
| `seen` | 累计已报告过的 `id`。跨次保留，只增不删 |
| `brief` | 本次简报的绝对路径 |

每次跑完覆盖写入。`seen` 里已有的 `id`：不重抓原文、不重评结论（本轮刚按旧规则跑过、用户要补介绍的除外：用已写入的 `board` 补跑，不再取榜）。无日志则 `seen` 当空。本次榜前 20 的 id 全部写入 `seen`。

## 取榜

1. 读日志取 `seen`（补跑今天已有 `board` 时跳过本步）。
2. 打开 [https://www.skills.sh/trending](https://www.skills.sh/trending)（WebFetch；页面不够再 `curl.exe`）。**不要**调 `/api/v1/skills`（要鉴权）。
3. 按页面顺序取 skill：`name`、`source`、`installs`、页面链接。同一 pack 的 `+N more` 按出现顺序展开。凑满 **20 个不重复 `id`** 即停。`id` 用 `{source}/{name}`。
4. 本机已有名：个人 `~/.cursor/skills/*/SKILL.md` 的 `name`、插件缓存各 `skills/`（或 `skills-figquery/`）子目录名、`~/.cursor/skills-cursor/` 子目录名。这些仍写一句「本机已有」，不抓原文。
5. `source` 含 `larksuite`、`feishu`、`azure-skills`、`heygen`、`runcomfy`、`hyperframes`、`marketingskills`：仍写一句它干什么（用榜页摘要即可），结论 `放下`（黑名单），不抓原文。
6. `seen` 里的 id：不重抓、不重评；简报与报告里的用途怎么留，见「简报」。

## 介绍与深评

对剩下的**每一条**都要够到「它干什么」：

1. 先抓 `SKILL.md`（步骤见「落盘原文」）。摘要页只在原文拿不到时用。
2. 用 1～2 句写清它解决什么任务，不要只重复名字。
3. 标命中的词（可空）。词表只表示更贴近本机栈，**不是**介绍资格。
4. 再给结论。写得出「更好在哪」才并进 / 新建；写不出就 `放下`，原因写在「干什么」之后。

同栈（`self-python-*`、`self-react`、`playwright-cli`、`web-clone`、`self-notes-read`、`writing-for-agents`、`self-code-principles`）优先深评并进。明确另一产品栈结论倾向 `放下`，但仍要那句用途：Next App Router 专用、React Native / Expo、Vercel 部署 / 计费、Firebase、Flutter、把 Django / Flask / PyPI 发版当默认、纯 AI 绘图/视频/音乐生成管线。

安装量只作榜上事实。同一套内容的镜像仓（name 相同、source 不同）第一份写用途，其余点明「镜像，用途同上」。

## 落盘原文

存到 `<工作目录>\skills-docs\find-skills\<YYYY-MM-DD>\<source 斜杠换成->__<name>.md`。文件顶部三行写来源 URL、`installs`、抓取方式（`raw` / `tree` / `page`）。镜像仓若与已抓的正文相同，可只落第一份，简报互指。

抓取顺序，取第一个 200 且正文像 SKILL.md（有 `name:` 或开头 `#`，不是 `<!DOCTYPE html>`）的：

1. `https://raw.githubusercontent.com/<source>/HEAD/skills/<name>/SKILL.md`；也试仓库根 `<name>/SKILL.md`、`tools/<分类>/<name>/SKILL.md`（以及 `plugins/<plugin>/skills/<name>/SKILL.md`）
2. 用 jsDelivr 列仓库文件：`https://data.jsdelivr.com/v1/packages/gh/<source>@main`，找以 `/<name>/SKILL.md` 结尾的 path，再拉 `https://raw.githubusercontent.com/<source>/HEAD/<path>`。**不要**用 GitHub `git/trees` API（未认证容易 403）
3. `https://skills.sh/<source>/<name>`：只抽出页面上的摘要 / SKILL 预览，**禁止把整页 HTML 落盘**；文件里标注 `page（截断）`

`references/` 下的子文档不抓。跑 Python 用 `<conda 根>\python.exe` + `PYTHONIOENCODING=utf-8`，不要 `conda run`。PowerShell 里 `curl` 是 `Invoke-WebRequest` 的别名，用 `curl.exe`。

## 评估：只说更好在哪

「更好在哪」= 它对哪个分叉给了本机没有的动作，或同一件事给了更锐的判据。写不出这一句就是 `放下`。

不要写「本地已经更好」的对比论证。远程默认与本机硬约束冲突时（验证由用户手动执行、小服务目录用 `self-python-project`、页面验收用几何测量与真点），**只取它能用的那部分**当建议，冲突点一句话标注即可。

| 结论 | 何时 | 要写出什么 |
|------|------|-----------|
| **并进** `某skill` | 目标文件在这个分叉上沉默，且这句话会改掉模型默认行为 | 落点文件 + **要加的那一句原文**（可直接粘进去） |
| **新建** `<名字>` | 现有 skill 没有这条独立触发，规则可执行且够多 | 建议的 `name`、description 里的触发词、正文要有的 3～5 条 |
| **笔记** | 教材、API 目录、模式清单 | 落到 `笔记库` 哪个主题 |
| **放下** | 本机已覆盖、空操作、或纯另一产品栈 | 一行原因 |

并进两条闸门：一句能写清且完成与否可核查；落点就是那份文件（会话索引只接 PATH 白名单，风格与跑法进 `self-python-style`，函数与 FastAPI 进 `self-python-function`，切步进 `self-python-script`，目录形态进 `self-python-project`，页面与验收进 `self-react`，网站复刻进 `web-clone`，兜底判断进 `self-code-principles`）。

## 简报

写 `<工作目录>\skills-docs\find-skills\<YYYY-MM-DD>-brief.md`，同一天重跑就覆盖。覆盖时 `seen` 条目**沿用当日已有简报里的「干什么」和结论**（可加「本次不重评」）；跳过的是重抓与重评，介绍留在简报和给用户的报告里。

```markdown
> 归纳日期：<YYYY-MM-DD>
> 外部文档
> 来源：https://www.skills.sh/trending 前 20 + 各条 SKILL.md / 页面摘要（路径见正文）

# find-skills <YYYY-MM-DD> 简报（trending | trending-keyword）

## 本次怎么跑的
榜前 20、词表怎么用、跳过了什么、原文落在哪个目录。

## 可以马上落地的
并进与新建，一条一段。没有就写明 0 条。

## 榜前 20
每条一行或一小段：name、source、installs、干什么、命中的词（可空）、结论、原文文件名（有则写）。
```

## 报告

向用户先给「可以马上落地的」，再按榜顺序介绍这 20 条（干什么 + 结论；`seen` 条目用简报里沿用的那几句），最后给简报与原文目录的路径。并进为 0 时写明这次没有过闸的短规则。

本机 skill 用对照，不 `npx skills add`。用户说「改文件」后，只把过闸的并进写进对应 skill；写法见 `writing-for-agents`。`<用户目录>\.dsh\skills\` 里若有同名 `SKILL.md` 则一并改。
