# skill 的调用机制

本仓工作树（`skills/`）里，一个 skill 怎么被够到、命令从哪来、细则收到哪去。

## 两种调用方式

两种方式交换的是同一份预算：常驻成本（每轮都在烧 token）与人的记忆负担（得记住有哪些文档）。

- **模型可触发**：留 `description`，agent 自己够得到，别的 skill 也指得动。description 是 skill 顶层的指针，被迫常驻：拿常驻成本换可发现性。做法：不写 `disable-model-invocation`，description 面向模型写、带全触发分支。
- **用户触发**：设 `disable-model-invocation: true`，把 skill 从 agent 的目录里摘掉，只有人打名字能进。零常驻成本，代价全落在人身上——你是唯一记得它存在的索引。description 这时面向人写：一行摘要，去掉触发清单。

只有 agent 必须自己够到、或别的 skill 必须指得动时，才选模型可触发。

## 命令从哪来

给人打命令触发的 skill，在 description 末尾带 `命令：/<名字> —— 一句话作用`；开场清单从 `available_skills` 现抄，不另存一份（另存的那份会漂移）。

**一条命令 = 一个 skill 条目**：`/名字` 手势只认目录里某个用户可调用的 skill 名，一个 skill 只有一个名字。反过来也成立——一个 skill 只有一条命令。所以别为了多给几条命令就拆出几个只为挂命令的壳 skill。

**不挂命令也是对的**：只给模型够、人不常手打时，就不加那条尾巴——零常驻成本，也不用维护一张人会忘的命令表。本仓 `self-skill-crud` 就没挂：写 skill 时模型自己够得到，它的边界是确定的；四件事的分流写在它自己的正文里，认出是哪一件之后读 `references/` 下对应那一份。要是它该触发时没触发，那是 skill 的缺陷——按 `references/update.md` 改它自己的 description，不要靠加命令去补。

## 细则收到哪去

分类入口把细则收进自己目录时，被收的入口文件必须叫 `BODY.md`，**不能**叫 `SKILL.md`：DSH 只认扫描根顶层的 `<名>/SKILL.md`，嵌套的 `SKILL.md` 刻意不发现；Cursor 却会递归扫所有 `SKILL.md`，分类目录挡不住。

先例：`self-frontend/self-react/BODY.md`、`self-frontend/web-clone/BODY.md`、`self-spyder/playwright-cli/BODY.md`。

## 共享参考放哪

两个用户触发的 skill 都要用同一份参考、两边都放不下时（它们没有 description，谁也指不动谁），把参考推到 skill 目录里的普通文件，两边各留一句指针。

先例：`self-session-bootstrap/agent-dsh.md`、`self-session-bootstrap/agent-cursor.md`、`self-session-bootstrap/agent-codex.md`。
