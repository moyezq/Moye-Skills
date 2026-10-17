# 个人 Skills 系统

个人 skill 的术语表：正文只在工作树一份，远程事实源是技能仓。agent 开场读会话索引。这里只收本系统特有的叫法。

## Language

**技能仓**：
GitHub 上的 `Moye-Skills` 仓库，个人 skill 的单一远程事实源。
_Avoid_: 两份 skill, 同步目录, skills 备份

**工作树**：
本仓 `skills/` 目录。各产品的个人 skills 路径用目录联接指向它，不是第二份拷贝。
_Avoid_: 双 clone, 同步一份到另一端, 仓根平铺

**skill 根目录**：
加载本文件时给出的那一层，即**单个 skill 自己的目录**（`<工作树>/<名字>/`）。各 skill 正文里的 `<skill根目录>` 都指这一层，`scripts/`、`references/`、各 harness 文档都在它下面。
_Avoid_: 拿它指工作树, 把它当 skills 仓根

**本机配置**：
未进仓的 `.env`，只放各产品 skills 目录的本机路径。模板是 `.env.example`。
_Avoid_: 写进 README 的盘符路径

**仓对齐**：
要对技能仓做 git 时，按会话索引第 7 步读的那份 harness 文档（`agent-dsh.md` / `agent-cursor.md` / `agent-codex.md`）里的 Git 一节执行。不是开场动作，不是日探测。
_Avoid_: 开场对齐, 开场探测, 日探测

**会话索引**：
新对话开场必须加载的那一份 skill（`session-bootstrap`）。它是开场步骤、进程级硬约束、个人 skills 命令清单的同一份正文。开场读这一份。各 harness 的操作规范在 `session-bootstrap/` 下按 `AGENT` 各一份：`agent-dsh.md`、`agent-cursor.md`、`agent-codex.md`，开场第 7 步读对应那份。
_Avoid_: 规范总览, 开场检查单, skills 总文档, session-tools, self-session-bootstrap（旧名）

**session-tools**：
工作树顶层 skill：本轮会话自检、交接（写/接）、从本轮抽可迁移面试题。入口 `SKILL.md` 路由；细则在 `references/` 下三份 md。不是会话索引（`session-bootstrap`）；不是 skill 分析报告（`skill-analyse`）。
_Avoid_: self-session-audit, self-session-handoff, self-interview-question（并入后的旧名）, 会话工具包

**会话标题**：
开场拟的索引行，格式 `MMDD | type | Title`。写在第一条回复顶上；产品若无能改会话名的工具，由人复制。
_Avoid_: 聊天名, 话题标签

**环境卡**：
按日历日缓存的最小本机事实，内容只有可用命令名与 conda 环境名。
_Avoid_: 两拍, 两拍结果, env_available.json, session_env.json, 环境扫描, which

**日探测**：
环境卡对应字段的日期不是今天时，才执行的那次命令探测或 conda 环境名探测。
_Avoid_: 两拍, 开场探测, 可用性探测

**命令白名单**：
以环境卡当天命令清单为准、允许在 Shell 里调用的第三方命令集合。开场正文也称「系统命令白名单」。
_Avoid_: 白名单（当用来单指这份清单时）, PATH, 可用命令列表, 两拍结果

**self-***：
个人编写、经工作树共用的 skill。与 Cursor 产品 skill（`skills-cursor`）相对。仅一端会读的 skill 仍算 self-*，何时 Read 由各自的 description 定。目录名不必带 `self-` 前缀（如 `session-bootstrap`、`skill-crud`）。
_Avoid_: 自定义 skill, 个人规范

**skill-crud**：
工作树顶层 skill：个人 skill 的增删改查（建 / 改 / 删 / 找）。入口 `SKILL.md` 认场景；细则在 `references/`。
_Avoid_: self-skill-crud（旧名）

**命令**：
description 末尾的 `/名字`，人打它触发该 skill；开场清单从 `available_skills` 现抄，不另存一份。
_Avoid_: 路由表, 触发条件表, 叠用关系

**固定上下文开销**：
每轮都躺在上下文里、不触发也照烧的 token 与注意力。skill 的 description、`AGENTS.md` 的一行都花这份预算。
_Avoid_: 常驻成本（旧名）, 上下文负载, 常驻 token

**指针**：
一句话带上「何时去够它」的条件。两类不要混：**触发向**（`description`：何时够到本 skill）与 **材料向**（正文里点名 `references/` 等：读哪份细则）。材料路径只进正文，不进 description。
_Avoid_: 上下文指针, 引用（当用来混指这两类时）

**渐进披露**：
正文只留每条路径都要的步骤，把只有部分路径需要的细则推到单独文件、靠指针够到。为的是保住顶层的可读层级，不是省 token。对应英文 progressive disclosure。
_Avoid_: 逐层往下推（旧名）, 信息层级, 披露参考

**完成标准**：
一个步骤干完的条件，写清「完成」与「未完成」的边界。既可核查又穷尽的那种最强。
_Avoid_: 验收标准, 判据（当用来指步骤终点的那个条件时）

**锚词**：
模型预训练里已有的紧凑概念，在正文里当词反复出现，用最少的 token 锚住一整片行为。
_Avoid_: 引导词, leading word

**无效指令**：
模型默认就会照做的指令，花了固定上下文开销换零行为改变。判据是「改不改默认行为」，相对模型、不相对读者。
_Avoid_: 废话指令（旧名）, 空操作, no-op

**提前收工**：
步骤没做完，agent 自己宣布完成。根因通常是完成标准模糊，先打磨边界；边界不可约模糊且确实观察到提前收工，才把后续步骤推出视野。
_Avoid_: 抢跑（旧名）, 提前完成, premature completion

**浏览器自动化**：
playwright-cli 自己启动 Chromium 就能点完的界面测试时读 `playwright-cli`。要接到已经在跑的浏览器、或依赖用户日常登录态取当前页时读 `web-crawler`。
_Avoid_: 浏览器入口, self-spyder（已退役）

**清单**：
给人看的薄索引（`skills-list.md`）：路径、分组、一句话。不复述何时 Read。
_Avoid_: 触发条件, 何时读

**skill 分析报告**：
技能仓 `analyse/<skill名>.md`：给人读的上游/本地 skill 拆解（简介、安装与命令、源码结构、核心原理、分步举例）。由用户触发的 `skill-analyse` 产出。不是笔记库，不是 `SKILL.md`。
_Avoid_: 外部文档（分析报告文头只写来源）, 知识库文

**最小视图**：
把项目、模块或代码文件收成能说清关键点的可视化。选型在 `project-docs` 的 `SHOW-FORMAT.md`。不是目标态蓝图（`architecture.md`）。
_Avoid_: 状态图（当用来指这份产物时）, show-me, 架构图（口语落到文件仍叫最小视图）

**兜底**：
写代码时默认生效的通用判断层（`code-principles` 的 13 条）。更专门 `self-*` 只在冲突点覆盖它，不是整份跳过。
_Avoid_: 默认规范, 通用原则（当用来表示「有专门 skill 就别读」时）, 过度兜底（字段访问场景，见信任上游）

**信任上游**：
按调用方已固定的字段名与结构直接访问，不为未知形状写多重类型判断和默认值。
_Avoid_: 过度兜底, 防御性取值

**空壳函数**：
只被一处调用一次、除了起名别无规则的函数或方法。
_Avoid_: 薄包装（旧名）, helper, 私有方法（当用来指这种一次性包装时）

**stepN**：
单文件脚本里按 0、1、2… 排列的阶段函数；一个 `stepN` 做完**一步处理**——一次请求或一次明确的数据变换，加上取字段、打印、本步产出。不要按感觉上的函数个数或「阶段」空名来切。
_Avoid_: 数据跳（旧名）, run, fetch_all, 主流程函数, 函数粒度, 阶段（当用来表示感觉上的分块而非一步处理时）

**契约**：
样例 JSON、`scheme`、联调 POST body 钉死的字段名、路由和配置名。改代码前先统一，不要半套新名。
_Avoid_: OpenAPI, 类型定义（当用来指这整链时）

**对照项目**：
已经能跑的开源 App、插件、阅读器或另一套爬虫。只当说明书读，不改上游仓库。
_Avoid_: 参考实现, 抓包（当用来指这份能跑的源码时）

**协议**：
一组会一起出现的主机发现、path、头、签名、分页。同一站点可有多条，先对照再选一条落地，不要混头、混 path。
_Avoid_: API（当用来指这整组时）, 抓包域名

**reverse-skill 包**：
dsh 插件仓里封装的那 87 份上游 `SKILL.md`（领域 + CTF）。本仓当对照项目读，不是工作树里的个人 skill。
_Avoid_: reverse-skill（当用来指将要写进工作树的那几份时）, 87 技能, 渗透平台

**改写收编**：
把对照项目里需要的能力按 `self-*` 写成少量个人 skill，经工作树两端共用。不是原样拷贝、不是全书中译、不是 dsh 插件另接一份。
_Avoid_: 本地化, 原样灌入, 中译后使用

**对照还原**：
弄懂或复现目标：对照源码还原协议、页面 JS 签名/加密、Android APK、按网页前端样式复刻。不是利用链、主动扫描、域渗透或 CTF 赛道。
_Avoid_: 分析向逆向（旧名）, 逆向工程（当用来统称 reverse-skill 全包时）, 渗透, 打穿

**独立 skill**：
不依赖笔记库或 reverse-skill 包就能执行的个人 skill。笔记里有、skill 没有的规则，写进 skill；别的 skill 可以指向它，它不能指向笔记才能开工。
_Avoid_: 指向笔记, 技能包当运行时依赖

**两套请求头**：
同一协议里 JSON/目录 与 文件/CDN 各用一套 HTTP 头。元数据签名不要打到拉文件的请求上。
_Avoid_: 请求身份（旧名）, UA, Cookie（当用来统称这两套头时）

**归纳日期**：
知识库文档头里的 `YYYY-MM-DD`。等于今天且用户未点名该文件/主题时，跳过 Read 全文。
_Avoid_: 修改时间, mtime

**外部文档**：
文首标 `> 外部文档` 的第三方总结稿。默认近原稿，须保留 `来源`；无明确修改授权不按本库文风整篇改写。
_Avoid_: 参考资料, 课件来源（截图/口播是材料，不是这一类）

**知识链**：
指向可吸收进正文的讲解页。有价值内容写入对应章节后再删链接。
_Avoid_: 资源链（下载页、Releases、数据集、外部文档的来源须保留）

**镜像类型**：
后端契约字段在前端的同名 TypeScript 类型。只跟随契约，不另起一套字段名。
_Avoid_: DTO, 前端自己的接口（当用来指这份镜像时）

**单滚动条**：
固定区域里只有内容超出的那一层 `overflow`。子块各自加滚动会把该读的长文本压没。
_Avoid_: 整页滚动, 每个块都 overflow
