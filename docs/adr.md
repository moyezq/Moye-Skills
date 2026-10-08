# 架构决策（现行）

现行约束在 [`CONTEXT.md`](../CONTEXT.md)、[`skills-list.md`](../skills-list.md) 与各 `skills/*/SKILL.md`。本文只记仍有效的为什么。废决策见 `HISTORY.md`。

## ADR-0001 · 2026-09-20 · 一份工作树，两端目录联接

多个 agent 产品不要各维护一份 skill 拷贝。clone 本仓后，把各产品的个人 skills 目录联接到本仓 `skills/`。两头各自 clone、靠 push/pull 互相同步，同机仍会漂。

## ADR-0002 · 2026-10-01 · 仓对齐只快进；用户说「同步」才 commit + push

对技能仓做 git 时，落后且工作区干净则 `pull --ff-only`；用户说「同步」＝授权把全部改动 commit 一条（报文件清单与 message）并 `git push`；其余情况超前只问、分叉或 dirty 只报告。不自动 merge / rebase，没被要求时不 commit。按日历日缓存会拿到过期 skill；自动合并会把未审视的分叉写进工作树；攒下的改动该不该进历史由用户拍。何时执行见 ADR 0004。

## ADR-0003 · 2026-09-20 · skill 放在 skills/ 子目录

仓根留给 README、本机配置模板、术语表和 ADR。产品扫描的是带 `SKILL.md` 的目录；把 skill 平铺在仓根会把文档和 git 元数据混进扫描范围。联接目标是 `skills/`，git 在仓库根。

## ADR-0004 · 2026-10-08 · 仓对齐不做开场动作

每条新对话都 fetch，会把 git 状态机压进开场；多数对话不操作技能仓。git 规则随当轮 harness 那份文档在开场第 7 步可读，但**开场不跑任何 git 动作**；要对技能仓做 git 时，才按它那一节走。快进与「同步」授权仍按 ADR 0002。

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

## ADR-0015 · 2026-10-07 · 桌面壳界面单独立一份 self-desktop-ui

窗口、标题栏、材质、托盘、全局热键、单一实例、IME 候选框、原生右键菜单属于**壳层**，不是页面内部的事。工作树顶层新增 `self-desktop-ui` 收这一层，`self-frontend` 继续管页面、组件、布局；两份用指针相连，各管一层。正文按 Windows 写，附 WebView2 / Electron / Tauri 三栈的能力对照。

备选是并进 `self-frontend` 当一个分类目录。否掉的理由有两条：其一，`self-frontend` 的作用域是网页前端，硬塞要付双份代价——抬高它的层级，读它的人还得跳过不属于它的段落；其二，壳层有一半内容在原生侧（DWM 材质、Win32、IME 焦点归属），跟「写 React 页面」不是同一批动作。

上游两份（`yetone/native-feel-skill`、`pbakaus/impeccable`）按改写收编处理，不原样搬：抽掉上游的四层架构、UniFFI、内存核算与整套 CLI，改用本仓的中文写法与完成标准。上游在若干处互相冲突（系统字体 vs 自定义字体、骨架屏 vs 转圈、悬停统一 vs 分控件），取舍按「等价原生控件怎么做」这一条判据裁决，结论写进正文与 references。

## ADR-0016 · 2026-10-08 · 操作规范按 harness 自包含，开场读对应那一份

`AGENT` 决定用哪套工具与沙箱，「读文件 / 改文件 / 跑 Python / Git / 提权 / 后台」这六块在每个 harness 里的做法都不同。决定：`self-session-bootstrap` 同目录按 harness 各一份——`agent-dsh.md` / `agent-cursor.md` / `agent-codex.md`，每份自包含这六块；会话索引开场第 7 步按 `AGENT` 只读对应那份（`其它` 不读，按自带工具照通用做法）。只写实测过的做法，没实测的段落明写未实测。它取代 ADR-0014 的「两份按操作分的并列文件」，两份旧文件删除。

为什么：一个会话只该读自己那套命令。按操作分家时，「跑 Python」与「改文件」的 harness 差异摊在两份文件里，git 走法又单占一份，一个会话常要读两份才拼得出全貌；按 harness 自包含后，工具名、提权方式、git 走法在同一页。代价是共用条款（新建直接写、先读后改、生成文件不手改）与 git 状态分派在三份里各出现一次。

被否的备选：① 保留两份按操作分的文件——就是被取代的形制；② 共用条款与 git 状态分派只写一份、三份 harness 文档指过去——少三处重复，但一个会话要跳两个文件才动手，与自包含的目标相反。

## ADR-0017 · 2026-10-09 · 退役 self-video-notes

用户实测结论：`self-video-notes`（本地 mp4 / B 站链接转 SRT + Markdown）**几乎用不到，对目标任务的帮助也不大**，直接删除。工作树顶层 skill 从 19 个降到 18 个，`CONTEXT.md` 的「视频笔记」词条一并删掉；连带面只有两处活指针（`skills-list.md` 清单行与那行计数、`CONTEXT.md` 词条），已同轮清完。

为什么不留着：它的正文全是本机专属值（ffmpeg / whisper / yt-dlp 的绝对路径、`asr` 环境、medium.pt 模型目录），而这些值又要指向工作区里**另一个项目**（`Individual/whisper`）——既常年占 description 的常驻成本，又是跨项目泄漏的来源。退役比改成通用版划算：它服务的场景（把视频转成笔记）在本仓没有第二个用户。

被否的备选：① 改成通用版留着（ffmpeg / whisper 路径挪进 `.env`）——用户判它连场景都不常用，为它维护一份 `.env` 契约不值；② 移进 `backup/` 暂存——本仓 `backup/` 已有 10 份对照实验留档，再塞一份没在用、也没在对比的 skill 只会堆陈旧层。真要复活，`git log` 里有全文。
