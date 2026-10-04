# 架构决策（现行）

现行约束在 [`CONTEXT.md`](../CONTEXT.md)、[`skills-list.md`](../skills-list.md) 与各 `skills/*/SKILL.md`。本文只记仍有效的为什么。废决策见 `HISTORY.md`。

## ADR-0001 · 2026-09-20 · 一份工作树，两端目录联接

多个 agent 产品不要各维护一份 skill 拷贝。clone 本仓后，把各产品的个人 skills 目录联接到本仓 `skills/`。两头各自 clone、靠 push/pull 互相同步，同机仍会漂。

## ADR-0002 · 2026-10-01 · 仓对齐只快进；用户说「同步」才 commit + push

对技能仓做 git 时，落后且工作区干净则 `pull --ff-only`；用户说「同步」＝授权把全部改动 commit 一条（报文件清单与 message）并 `git push`；其余情况超前只问、分叉或 dirty 只报告。不自动 merge / rebase，没被要求时不 commit。按日历日缓存会拿到过期 skill；自动合并会把未审视的分叉写进工作树；攒下的改动该不该进历史由用户拍。何时执行见 ADR 0004。

## ADR-0003 · 2026-09-20 · skill 放在 skills/ 子目录

仓根留给 README、本机配置模板、术语表和 ADR。产品扫描的是带 `SKILL.md` 的目录；把 skill 平铺在仓根会把文档和 git 元数据混进扫描范围。联接目标是 `skills/`，git 在仓库根。

## ADR-0004 · 2026-10-01 · 仓对齐按需加载，不开场必做

每条新对话都 fetch，会把 git 状态机压进常驻开场；多数对话不操作技能仓。git 步骤写在会话索引同目录 `agent-git-op.md`，仅本轮要对技能仓做 git 时读。快进与「同步」授权仍按 ADR 0002。

## ADR-0005 · 2026-09-20 · 分析向逆向改写收编，不灌入 reverse-skill 包

工作树只收按个人规范改写的分析向逆向 skill（协议/JS 与 APK/移动）。87 份 reverse-skill 包留作对照项目，不原样拷进 `skills/`，也不靠 dsh 插件给 Cursor 补能力。两端仍走现有目录联接。

排除 CTF 赛道、攻击链、渗透工具、EDR 绕过。原包路由器会立刻跑脚本、与会话索引和手动验证冲突，改写时不继承。

## ADR-0006 · 2026-09-20 · 个人 skill 独立可执行，不把笔记当运行时依赖

分析向逆向 skill 必须单独能用。笔记库 给人读；笔记里有而 skill 没有的规则，吸收进 skill，不在 SKILL.md 里要求先打开某篇笔记。reverse-skill 包同样只作改写时的对照，不写进执行路径。

其它 skill 可以指向这些独立 skill（例如脚本切步指向协议还原）。不要反向依赖笔记路径，尤其不要写盘符。

## ADR-0007 · 2026-09-20 · protocol-reverse 以对照项目还原 HTTP 为主路径

`protocol-reverse` 的「协议」取本仓定义：从能跑的对照项目抽出一组 HTTP 行为。上游 reverse-skill 里同名模块偏 PCAP / 二进制帧 / Protobuf，那些作为 references 分支，不是主入口。

没有对照源码、只有页面 JS 时走 `js-reverse`。协议已清、要写分阶段脚本时走 `self-python-script`。

## ADR-0008 · 2026-09-20 · web-clone 算分析向逆向第四条

网页按前端样式复刻与协议/JS/APK 同属分析向逆向，不是渗透，也不是普通 UI 走查。`web-clone` 只还原外观、交互和 WebGL 效果；接口签名和对照协议仍走 `js-reverse` / `protocol-reverse`。清单与四份 skill 的应用场景表按四选一互指。

## ADR-0009 · 2026-10-01 · 最小视图并入 self-project-docs

把「用最小视图讲清结构」收进 `self-project-docs`，不再作为独立 skill。`architecture.md` 只收清单和文字；现状图走 `docs/overview.md`（密 UI 用 `.html`）等最小视图文件。独立 `show-me` 从工作树删除。

备选是保留独立 skill，或把图写进蓝图。否掉是为了单一入口，并分开现状可视化和目标态蓝图。

## ADR-0010 · 2026-10-01 · 前端入口 self-frontend

工作树顶层只留 `self-frontend` 的 description。前端任务先读这一份，再按其表读目录下的 `self-react` 或 `web-clone`。两份被收 skill 正文不改，整目录挪进 `self-frontend/`。入口文件必须叫 `BODY.md` 不能叫 `SKILL.md`：Cursor 递归扫描所有 `SKILL.md`，嵌套分类目录挡不住。点选走查走 `self-spyder`（其下 `playwright-cli`）。

备选是三份平铺，或把细则抄进入口。否掉是为了渐进披露：入口薄、细则仍在原文件。

## ADR-0011 · 2026-10-01 · 浏览器入口 self-spyder

工作树顶层只留 `self-spyder` 的 description。浏览器自动化、页面快照、UI 走查先读这一份，再读目录下的 `playwright-cli`。被收 skill 正文不改，整目录挪进 `self-spyder/`。入口文件必须叫 `BODY.md` 不能叫 `SKILL.md`：Cursor 递归扫描所有 `SKILL.md`。整站复刻仍走 `self-frontend`。

## ADR-0012 · 2026-10-01 · grilling 并入 grill-with-docs

拷问访谈与按落点沉淀文档不再拆成两份 skill。工作树只留 `grill-with-docs`：访谈原语在正文里，结晶了再加载 `self-project-docs` 或 `self-notes-read`。独立 `grilling` 从工作树删除。

备选是继续两份（访谈一份、沉淀一份）。否掉是因为每次对齐几乎都要沉淀，拆开会让 agent 只问不写。

## ADR-0013 · 2026-10-01 · skill 路由靠 description，不设路由表

会话索引正文不再维护「skill → 何时读」的路由表：同一信息已由 catalog 里各 skill 的 description 常驻，表是第二份会漂移的拷贝，占开场正文约三成。改为每条 description 末尾带 `命令：/名字`，开场输出从 catalog 现抄一行命令清单；组合与先后关系留在各自 description 里。

备选是保留路由表，或另设一个 router skill。否掉是因为两者都要额外维护一份与 description 同层的目录。
