# 架构决策（现行）

现行约束在 [`CONTEXT.md`](../CONTEXT.md)、[`skills-list.md`](../skills-list.md) 与各 `skills/*/SKILL.md`。本文只记仍有效的为什么。废决策见 `HISTORY.md`。

## ADR-0001 · 2026-09-20 · 一份工作树，多端目录联接

多个 agent 产品不要各维护一份 skill 拷贝。clone 本仓后，把各产品的个人 skills 目录联接到本仓 `skills/`。两头各自 clone、靠 push/pull 互相同步，同机仍会漂。

## ADR-0002 · 2026-10-01 · 仓对齐只快进；用户说「同步」才 commit + push

对技能仓做 git 时，落后且工作区干净则 `pull --ff-only`；用户说「同步」＝授权把全部改动 commit 一条（报文件清单与 message）并 `git push`；其余情况超前只问、分叉或 dirty 只报告。不自动 merge / rebase，没被要求时不 commit。按日历日缓存会拿到过期 skill；自动合并会把未审视的分叉写进工作树；攒下的改动该不该进历史由用户拍。何时执行见 ADR 0004。

## ADR-0003 · 2026-09-20 · skill 放在 skills/ 子目录

仓根留给 README、本机配置模板、术语表和 ADR。产品扫描的是带 `SKILL.md` 的目录；把 skill 平铺在仓根会把文档和 git 元数据混进扫描范围。联接目标是 `skills/`，git 在仓库根。

## ADR-0004 · 2026-09-20 · 个人 skill 独立可执行，不把笔记当运行时依赖

对照还原类 skill 必须单独能用。笔记库给人读；笔记里有而 skill 没有的规则，吸收进 skill，不在 SKILL.md 里要求先打开某篇笔记。reverse-skill 包同样只作改写时的对照，不写进执行路径。

其它 skill 可以指向这些独立 skill（例如脚本切步指向协议还原）。不要反向依赖笔记路径，尤其不要写盘符。

## ADR-0005 · 2026-10-01 · 最小视图并入 self-project-docs

把「用最小视图讲清结构」收进 `self-project-docs`，不再作为独立 skill。`architecture.md` 只收清单和文字；现状图走 `docs/overview.md`（密 UI 用 `.html`）等最小视图文件。独立 `show-me` 从工作树删除。

备选是保留独立 skill，或把图写进蓝图。否掉是为了单一入口，并分开现状可视化和目标态蓝图。

## ADR-0006 · 2026-10-01 · 前端入口 self-frontend

工作树顶层只留 `self-frontend` 的 description。前端任务先读这一份，再按其表读目录下的 `self-react` 或 `web-clone`。两份被收 skill 正文不改，整目录挪进 `self-frontend/`。入口文件必须叫 `BODY.md` 不能叫 `SKILL.md`：Cursor 递归扫描所有 `SKILL.md`，嵌套分类目录挡不住。点选走查走顶层 `playwright-cli`。

备选是三份平铺，或把细则抄进入口。否掉是为了渐进披露：入口薄、细则仍在原文件。

## ADR-0007 · 2026-10-01 · 浏览器入口 self-spyder

工作树顶层只留 `self-spyder` 的 description。浏览器自动化、页面快照、UI 走查先读这一份，再读目录下的 `playwright-cli`。被收 skill 正文不改，整目录挪进 `self-spyder/`。入口文件必须叫 `BODY.md` 不能叫 `SKILL.md`：Cursor 递归扫描所有 `SKILL.md`。整站复刻仍走 `self-frontend`。

## ADR-0008 · 2026-10-01 · grilling 并入 grill-with-docs

拷问访谈与按落点沉淀文档不再拆成两份 skill。工作树只留 `grill-with-docs`：访谈原语在正文里，结晶了再加载 `self-project-docs` 或 `self-notes-read`。独立 `grilling` 从工作树删除。

备选是继续两份（访谈一份、沉淀一份）。否掉是因为每次对齐几乎都要沉淀，拆开会让 agent 只问不写。

## ADR-0009 · 2026-10-01 · skill 路由靠 description，不设路由表

会话索引正文不再维护「skill → 何时读」的路由表：同一信息已由 catalog 里各 skill 的 description 常驻，表是第二份会漂移的拷贝，占开场正文约三成。改为每条 description 末尾带 `命令：/名字`，开场输出从 catalog 现抄一行命令清单；组合与先后关系留在各自 description 里。

备选是保留路由表，或另设一个 router skill。否掉是因为两者都要额外维护一份与 description 同层的目录。

## ADR-0010 · 2026-10-07 · 桌面壳界面单独立一份 self-desktop-ui

窗口、标题栏、材质、托盘、全局热键、单一实例、IME 候选框、原生右键菜单属于**壳层**，不是页面内部的事。工作树顶层新增 `self-desktop-ui` 收这一层，`self-frontend` 继续管页面、组件、布局；两份用指针相连，各管一层。正文按 Windows 写，附 WebView2 / Electron / Tauri 三栈的能力对照。

备选是并进 `self-frontend` 当一个分类目录。否掉的理由有两条：其一，`self-frontend` 的作用域是网页前端，硬塞要付双份代价——抬高它的层级，读它的人还得跳过不属于它的段落；其二，壳层有一半内容在原生侧（DWM 材质、Win32、IME 焦点归属），跟「写 React 页面」不是同一批动作。

上游两份（`yetone/native-feel-skill`、`pbakaus/impeccable`）按改写收编处理，不原样搬：抽掉上游的四层架构、UniFFI、内存核算与整套 CLI，改用本仓的中文写法与完成标准。上游在若干处互相冲突（系统字体 vs 自定义字体、骨架屏 vs 转圈、悬停统一 vs 分控件），取舍按「等价原生控件怎么做」这一条判据裁决，结论写进正文与 references。

## ADR-0011 · 2026-10-08 · 操作规范按 harness 自包含，开场读对应那一份

`AGENT` 决定用哪套工具与沙箱，「读文件 / 改文件 / 跑 Python / Git / 提权 / 后台」这六块在每个 harness 里的做法都不同。决定：`session-bootstrap` 同目录按 harness 各一份——`agent-dsh.md` / `agent-cursor.md` / `agent-codex.md`，每份自包含这六块；会话索引开场第 7 步按 `AGENT` 只读对应那份（`其它` 不读，按自带工具照通用做法）。只写实测过的做法，没实测的段落明写未实测。它取代 ADR-0014 的「两份按操作分的并列文件」，两份旧文件删除。

为什么：一个会话只该读自己那套命令。按操作分家时，「跑 Python」与「改文件」的 harness 差异摊在两份文件里，git 走法又单占一份，一个会话常要读两份才拼得出全貌；按 harness 自包含后，工具名、提权方式、git 走法在同一页。代价是共用条款（新建直接写、先读后改、生成文件不手改）与 git 状态分派在三份里各出现一次。

被否的备选：① 保留两份按操作分的文件——就是被取代的形制；② 共用条款与 git 状态分派只写一份、三份 harness 文档指过去——少三处重复，但一个会话要跳两个文件才动手，与自包含的目标相反。

## ADR-0012 · 2026-10-10 · 会话向三份 skill 并入 session-tools

把 `self-session-audit`、`self-session-handoff`、`self-interview-question` 合成工作树顶层一份 `session-tools`。三块都是「围着本轮会话干活」（自检 / 交接 / 从本轮抽面试题），共用一个入口；细则落在 `references/` 下三份 md，入口 `SKILL.md` 只做何时读哪一份。`session-bootstrap`（会话索引）与 `skill-analyse` 明确不进、本轮也不改。各块行为与落盘约定（审计脚本报告、HANDOFF 指针、`docs/questions` 四段结构）只搬家不改语义。

目录名用 `session-tools`（不加 `self-`）：用户点名。不挂 `命令：` 尾巴（与 `skill-crud` 同）：靠 description 里的触发分支让模型自己够到，正文用表路由到 `references/`。否掉的备选：① 继续三份平铺；② 薄入口 + 子目录 `BODY.md`（ADR-0006/0007 形制）——本回合的细则更像流程分册，收进 `references/` 与 `skill-crud` 一致；③ 把 `skill-analyse` 一并塞进来——作用域不是会话态；④ 挂 `/session-tools`——人很少手打这三件事，命令尾巴是多余的固定上下文开销。

## ADR-0013 · 2026-10-10 · 会话索引改名为 session-bootstrap

工作树里会话索引目录由 `self-session-bootstrap` 改为 `session-bootstrap`（去掉 `self-`），与 `session-tools` 同族命名。正文职责与开场七步不变；`name`、技能清单、术语表与活指针同轮改完。否掉继续叫 `self-session-bootstrap`：个人 skill 不必一律带 `self-` 前缀，会话向两份已用无前缀名。

## ADR-0014 · 2026-10-10 · skill 增删改查改名为 skill-crud

工作树里个人 skill 的增删改查目录由 `self-skill-crud` 改为 `skill-crud`。职责与四份流程不变；`name`、校验脚本路径、清单、README、`.env.example` 与活指针同轮改完。否掉保留 `self-` 前缀：与 `session-bootstrap` / `session-tools` / `skill-analyse` 同族无前缀命名。

## ADR-0015 · 2026-10-12 · playwright-cli 恢复顶层，退役 self-spyder

撤销 ADR-0007 的入口分层：`playwright-cli` 整目录回到 `skills/playwright-cli/`，入口恢复 `SKILL.md`；薄入口 `self-spyder` 从工作树删除。浏览器自动化、快照、走查由 catalog 里 `playwright-cli` 的 description 直接触发，不再经二级入口。否掉继续 `self-spyder` + `BODY.md`：多一层只分流、无额外判据，占固定上下文且与 ADR-0009「路由靠 description」重复。

## ADR-0016 · 2026-10-12 · self-python-testing 改名为 python-testing

工作树里 Python 测试 skill 目录由 `self-python-testing` 改为 `python-testing`（去掉 `self-`）。职责与三步流程不变；`name`、清单与活指针同轮改完。否掉保留 `self-` 前缀：与 `python-standard-coding` / `session-bootstrap` / `skill-crud` 同族无前缀命名。

## ADR-0017 · 2026-10-12 · self-project-docs 改名为 project-docs；正文不拿目录名当路由

工作树里项目文档 skill 目录由 `self-project-docs` 改为 `project-docs`。`skill-crud` 补硬规矩：跨 skill 优先点产物，真要分工点名时整份 skill 最多一条邻域入口，禁止在 `references/` 里把目录名抄成第二张路由表。改名后清掉 session-tools / plain-todo / grill 等处的重复互点。否掉全仓搜替换旧名：那会把坏模式固化进改名流程。

## ADR-0018 · 2026-10-12 · self-code-principles 改名为 code-principles

工作树里代码设计默认原则的目录由 `self-code-principles` 改为 `code-principles`（去掉 `self-`）。13 条正文与作用不变；`name`、description 里的冲突指针、术语表那一行的计数（12 条 → 13 条）、清单与活指针同轮改完。否掉保留 `self-` 前缀：与 `python-testing` / `session-bootstrap` / `skill-crud` 同族无前缀命名。

## ADR-0019 · 2026-10-12 · 退役 self-frontend 与 self-desktop-ui，材料落 backup/

`self-frontend`（含其下 `self-react`、`web-clone`）与 `self-desktop-ui` 从工作树退役，整目录移进新建的 `backup/`。三端目录联接到 `skills/`，移出即三端同时不再列出这两份；`setup.ps1` 只连到 `skills/` 根、不枚举 skill，不改。退役原因：两份都要重构，重构版赶不上各自项目的公开计划；本轮先退出工作树，内容留 `backup/` 备用，重构版落地时再收回 `skills/`。

落点选 `backup/` 而否掉 `preinstall/`：后者是上游第三方待审区，已 gitignore（`.gitignore`、README、`.env.example` 三处都写「不入仓」），自家 skill 退役要留在仓里可追溯；`SOURCES.md` 里 `backup/find-skills/` 是同形先例。也否掉 `git mv` 进 `preinstall/` 保留跟踪：那要把「不入仓」那三处说明改掉，把 preinstall 撑成两类落点。

连带同轮改完：`CONTEXT.md` 删「前端入口」「桌面壳」两条术语；`skills-list.md` 删前端、桌面两个分组；`playwright-cli` 的 description 去掉「整站复刻/仿站走 self-frontend」；`DOC-MAP.md` 去掉「实现手法走前端入口 skill」；`code-principles` 的冲突指针只留 `python-standard-coding`；`skill-crud/references/mechanics.md` 的 `BODY.md` 先例改指 `backup/`；`SOURCES.md` 两条去向列改指 `backup/self-desktop-ui`。ADR-0006 / 0007 / 0010 是当时的决策记载，不动。

## ADR-0020 · 2026-10-14 · web-crawler 装入 skills；playwright-cli 只做自动化测试

`web-crawler` 从 `preinstall/` 迁入 `skills/`。取有登录墙、验证码、反爬站点的当前页，走用户本机 Chrome 的一条 CDP 连接。`playwright-cli` 的 description 收窄为对本仓库或公开演示页做自动化测试，不再作为「打开任意网站看看」的默认入口。否掉继续把两者叠在 `attach --cdp=chrome`：开关模式下这条命令和 `tab-list` 会挂死。

## ADR-0021 · 2026-10-14 · playwright-cli 只覆盖自己启动的 Chromium

`playwright-cli` 的用/不用从「本仓库或公开演示页」改成能力判据：只有这条 CLI 自己 `open` 拉起的 Chromium 里就能做完的任务才用。接到已经在跑的浏览器、或新开空白窗口做不完（缺用户日常登录态），都不走这份 skill。否掉继续用「本仓 / 公开演示页」当边界：本地登录表单在 CLI 自己的窗口里能填完，该用；公开站若要用户日常 Cookie，不该用。

## ADR-0022 · 2026-10-14 · dsh 的浏览器入口改用插件注入的 browser_* 工具

本机装了 `browser-skill-dsh-plugin`（0.3.2）与 `bsk` CLI（`%USERPROFILE%\.local\bin\bsk.exe`），扩展连在用户的 Chrome 上。dsh 的浏览器活（开网页、读页面、填表、走查界面、看请求与 console）优先走它注入的 `browser_*` 工具。

决定性判据是**要不要麻烦用户**：`web-crawler` 的原生 CDP 五步走 Chrome 开关模式，按连接弹 Allow，用户在每一轮都得在场点一次（实测 2.9s / 9.9s 连得上，也有 25s / 90s 完全静默）；插件的扩展连接是一次性人工步骤，连上之后同一会话又起了 3 次会话、零弹窗。两条路都驱动用户已登录的 Chrome，插件这条路省掉逐次授权。`playwright-cli` 仍是可用的浏览器自动化工具，只是它新开的 Chromium 拿不到用户日常登录态，dsh 上不作首选。

否掉在 dsh 上继续以 `web-crawler` 为默认入口：它的 CDP 五步已验证可行，保留给其它 harness，切换判据是授权成本而不是能力。

落点选 `skills/session-bootstrap/agent-dsh.md` 新增 §7：会话开场第 7 步每轮必读，能盖过 catalog 里 `web-crawler` 的默认触发。`CONTEXT.md` 的「浏览器自动化」术语条不动——它说的是有哪些可用工具，dsh 的优先级由本条与 §7 承接；`playwright-cli` / `web-crawler` 正文也不改。

## ADR-0023 · 2026-10-15 · Chrome 开关模式 Allow 按连接计，超时当没点

日常 User Data 走 `chrome://inspect/#remote-debugging` 时，勾选会留下开关，弹窗 Allow 是**每条新进来的 WebSocket 点一次**，不是按时间过期。同一条连接一直开着不用再点；脚本断开再连就再弹。握手超过 60 秒的默认解释是用户没点到 Allow，不按程序或网络排障，也不重连。

否掉给 agent 写「授权 N 小时」或超时自动重试：Chrome 136+ 在默认目录上会忽略 `--remote-debugging-port`，免弹只能换非默认用户数据目录，那不是本 skill 的默认路径。拦即将发出的请求必须复用已经打开的那一条连接（`references/chrome-network.md`），禁止每个子步骤各自握手。

## ADR-0024 · 2026-10-27 · 调研用的最小服务单独立一份 references/service.md

「给模型或外站接口起一个只听本机的 HTTP 服务」不属于生产标准：它要的是快速落地、弄清流程、验证猜测，先弄清这个场景做不做。它与「一次请求」「多文件项目」同级，是 `python-standard-coding` 的第三份场景文件：`references/service.md`。

`project.md` 的形态一律按生产标准：整体架构、模块分层、隐私安全、生产部署。调研用的最小服务是它的例外，不是它的子类，所以在 `project.md` 只留一条指回 `service.md` 的指针（通用规则 3），并把通用规则 4 的禁令收窄成「不要用 `python 子目录/xxx.py` 启动**产品**服务」。

否掉塞进当时那节 FastAPI 里的做法：那要把 router/schema、启动文件四件事逐条写例外，例外读起来比规则还重。（那几节后来独立成了 `prd-fastapi.md`，见 ADR-0025。）

也否掉并进 `script.md`：那份讲的是「跑完就退出」，服务要一直听，两套运行上限与入口形态混在一处。

代价是 `lifespan` 那条在 `prd-fastapi.md` 与 `service.md` 各出现一次。接受：两份面向不同场景，写服务的人不会先去翻生产项目的分层规则。

## ADR-0025 · 2026-10-27 · project.md 收窄到通用规则，其余全部归 prd-fastapi.md

`project.md` 只管「哪个项目都成立」的那一层：`conf/`、`.env`、`scripts/`、启动文件命名、`docs/`、依赖、README，通用规则若干条（当时十三条，见 ADR-0026）。它现在的标题是「Python 项目的通用规则」。

其余全部搬进 `references/prd-fastapi.md`：「层和模块怎么切：照 OSI 七层模型那种分法」及其参考目录树、「接口写在哪：`router.py` 与 `schema.py`」、「启动文件只做四件事」、「进程级资源放 `lifespan`」、「已有结构优先」、「前后端同仓」。判据是这些只在**生产后端服务**里成立——纯脚本项目、单文件工具没有分层可切，也有没前后端之分。

分工因此是四份：`project.md` 通用规则 → `prd-fastapi.md` 生产服务 → `service.md` 调研用的最小服务 → `script.md` 单文件脚本。代码写法仍归 `function.md`。

文件命名用 `prd-` 前缀标出「生产标准」，与 `service.md`（调研、验证）对立面呈现。备选是叫 `fastapi.md`，但与 `service.md` 并排时看不出哪个是生产、哪个是验证，只靠读正文分辨。

代价是目录树里的三处内部编号（「见第 3 条」「见第 5 条」）跨了文件，已改成显式指向 `project.md` 通用规则 3 / 5。

## ADR-0026 · 2026-10-28 · project.md 再砍六条：环境进 env.md，落位上移全局规范

ADR-0025 之后 `project.md` 有十一条，其中六条各有更好的归属：

- 第 5 条（没有前端时不建 `frontend/` / `backend/`）→ 并入 `prd-fastapi.md` 目录树的注解。那张树本来就只在前后端同仓时才画 `backend/`，再在 `project.md` 立一条是第二份说法。
- 第 7 条（先定模块清单再写代码）与第 11 条（已有结构优先）→ 上移 `SKILL.md` 全局规范，成为 S18 / S19。它们不是「项目」的事，改任何一个已有文件都适用。
- 第 8、9 条（依赖怎么写、默认 conda）→ 新建 `references/env.md`。conda 与 uv 都对，判据是场景：最小服务快速验证、开源给外部部署用 uv；脚本级验证、宿主已有重环境可复用用 conda。通用规则是沿用项目原有的，不为了统一增加工作量。
- 第 10 条（Agent 起的测试进程测完就停）→ 删。`session-bootstrap` 的全程约束已有同一条，放在项目规范里会让它看起来只对「新项目」生效。

`project.md` 因此剩五条：`conf/`、`.env`、`scripts/` 落点、启动文件命名、`utils/` 落点。它的定位收窄成「仓里哪个文件放哪」，不含「怎么写」的判断。

否掉把 `env.md` 并进 `SKILL.md` 全局规范：conda / uv 的选择要摆判据和场景，塞进一条 S 规则会把那条撑成两屏。
