---
name: project-docs
description: 项目文档。管仓库里 CONTEXT、adr.md、history.md、architecture.md、pipelines.md、engineering.md、todo.md、README、AGENTS.md 等什么时候读、什么时候改、什么时候必须照做。写或改根目录 README、用户嫌 README 难读时必读 README 人读写法。写或改 docs/todo.md、待办方向时必读 todo 写法。讨论术语、写目标架构、定本仓给 AI 的规矩、改启动方式或 UI 规范时用。最小视图：把项目、模块或代码文件整理成能说清关键点的可视化；clone 无架构图要看结构、用户要了解算法/调用链/组件边界/目录职责/数据流/改动差异、或一个英文单词指代的成熟方案（RAG/SaaS/ERP）时用。画一下、示意、用图讲、调用关系、数据流、show me、可视化讲清楚走本 skill。写代码若改了规范名称、决策、模块状态、主流程实现细节、端口入口或本仓禁令，同一轮改对应文件，不要攒着不改到下轮。触发词：项目文档、CONTEXT.md、ADR、architecture.md、pipelines.md、engineering.md、todo.md、待办、工程踩坑、目标架构、模块目录位置、术语、最小视图、README 难读、使用指南。不是笔记库。需求未对齐时先做拷问式访谈。不要一决策一个 ADR 文件。可交互分析面板走官方 canvas。
---

# 项目文档

管仓库里给人、给 AI 看的文档：**什么时候建、读、改、必须照做**。术语一经落定就写下规范名称；难逆转决策记 ADR；多模块项目动手前先画目标架构；主流程实现细节写 pipelines；现状用最小视图讲清。

仅仅「读 CONTEXT.md 查词」不是本 skill；本 skill 管的是**改文档并让代码遵守它**，以及用最小视图讲清现状。

## 何时用 / 何时不用

**用**：讨论术语；写或编辑下面「文档地图」里的任何文件；多入口 / 多模块 / 对照实验环境动手前画目标架构。项目里已有这些文件之一，且本轮代码改了规范名称、为什么、模块、启动方式、本仓 AI 禁令或主流程实现细节。最小视图见下节。用户要记本仓工程踩坑、写或改 `docs/engineering.md`。用户要写或改 `docs/todo.md`、待办方向。

**不用**：只读词、查定义；笔记库文；把开发经历抽成面试题；本轮只改函数内部，且不改规范名称、决策、模块、主流程实现细节、端口或入口（缺空检查、修打印）。单文件脚本不必建目标架构文档和 UI 文档。可交互分析面板 / 图表仪表走官方 `canvas`。

完成标准：本轮若改了某份文档所管的事，对应文件在同一轮已改。不把「下轮规范再改文档」当成完成。每份已存在的文档都按 [DOC-MAP.md](./DOC-MAP.md) 的读/改/遵守来用。本轮若写或改根目录 `README.md`：已按 [README-FORMAT.md](./README-FORMAT.md) 过一遍。本轮若写或改 `docs/engineering.md`：已按 [ENGINEERING-FORMAT.md](./ENGINEERING-FORMAT.md) 过一遍。本轮若写或改 `docs/todo.md`：已按 [TODO-FORMAT.md](./TODO-FORMAT.md) 过一遍。本轮若画了最小视图：已按 [SHOW-FORMAT.md](./SHOW-FORMAT.md) 选型；该落盘的已写到规定路径；图没有写进 `architecture.md`。

## 文档地图（先看这张表）

宁缺毋滥，用到再建。不要按清单一次建齐。文件名全小写。不要另建 `PROJECT-SPEC.md`、`ARCHITECTURE.md`、`docs/adr/`。

每份的建/读/改/遵守见 [DOC-MAP.md](./DOC-MAP.md)。格式见格式说明文件。

**`docs/` 标准四份**（软件仓目标集）：

| 文件 | 只收什么 | 何时建 |
|------|----------|--------|
| `docs/adr.md` | 真正关键的架构决策（现在为什么这样选） | 第一条值得记的决策 |
| `docs/history.md` | 过时但仍能提供有效历史信息的决策 | 第一次把过时决策从 adr 挪出 |
| `docs/architecture.md` | 核心功能是什么、核心模块有哪些、哪些暂时或明确不做 | 多入口 / 多模块 / 对照实验环境，动手写代码之前 |
| `docs/pipelines.md` | 主流程实现细节：各层、各模块、各方法里真正要紧的怎么做 | 主流程能按层/模块讲清、且细节不该挤进 architecture 时 |

**仓根**（给人跑、给 AI 例外、术语）：

| 文件 | 只收什么 | 何时建 |
|------|----------|--------|
| `CONTEXT.md` | 规范名称 | 第一个术语落定 |
| `README.md` | 给人上手跑：定位、分步上手、项目功能、不支持或需要额外条件、结构 | 第一条可跑通路径之后，或用户要使用指南 |
| `AGENTS.md` | 本仓给 AI 的例外与禁令 | 全局 skill 管不到的本仓硬规矩出现时 |
| `DESIGN.md` | 配色、间距、基础交互 | UI 超过单页简单问答，或用户要定视觉规范 |

最小视图按需：`docs/overview.md`（或 `.html`），不进标准四份，图不写进 `architecture.md`。

踩坑问答按需：`docs/engineering.md`，不进标准四份。本仓业务流程里真实踩过、且通用 skill 还没有写成规范的事故，第一次出现时再建。

待办方向按需：`docs/todo.md`，不进标准四份。本阶段打算做的方向；目标架构已有、出现第一条方向时再建。

改规范名称改 `CONTEXT.md`。新的关键决策**追加** `docs/adr.md`；过时且仍有用的挪到 `docs/history.md`；影响新决策判断的从 adr **删除**不进 history。改核心功能/模块/不做改 `architecture.md`。改主流程实现细节改 `docs/pipelines.md`。改怎么跑改 `README.md`。改本仓 AI 禁令改 `AGENTS.md`。本仓踩坑问答改 `docs/engineering.md`。改待办方向改 `docs/todo.md`。

## 文件结构

```
/
├── AGENTS.md
├── README.md
├── CONTEXT.md
├── DESIGN.md      # 按需
└── docs/
    ├── adr.md
    ├── architecture.md
    ├── history.md
    ├── pipelines.md
    ├── engineering.md  # 按需
    └── todo.md         # 按需
```

根目录存在 `CONTEXT-MAP.md` 表示多限界上下文。格式：[CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md)、[ADR-FORMAT.md](./ADR-FORMAT.md)、[ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md)、[PIPELINES-FORMAT.md](./PIPELINES-FORMAT.md)、[README-FORMAT.md](./README-FORMAT.md)、[ENGINEERING-FORMAT.md](./ENGINEERING-FORMAT.md)、[TODO-FORMAT.md](./TODO-FORMAT.md)。最小视图：[SHOW-FORMAT.md](./SHOW-FORMAT.md)。

不要往 `docs/` 再堆接口手册、运行手册、扩展手册。接口看运行中的 OpenAPI 与 README 的 `curl`；配置看 `.env.example`。

## 会话中怎么做

### 对照术语表挑战

用户用的词和 `CONTEXT.md` 冲突时立刻指出：「术语表把 X 定义为 …，但这里像在指 Y，是哪一个？」

### 打磨模糊用词

一词多义时给出规范词：「account 是 Customer 还是 User？这是两个东西。」

### 用场景加压

发明试探概念边界的场景，逼概念边界说精确。

### 与代码交叉核对

用户说「某功能是这样」时，对代码。本轮把目标架构里「未做 / 暂时不做」做成了已有能力，同一轮改 `architecture.md`。本轮改了主流程的判定、上限或字段落点，同一轮改 `pipelines.md`。

### 就地更新 CONTEXT.md

术语一解决就更新，不要攒着不改。`CONTEXT.md` 只收规范名称：代码变了若**定义**过时，改定义，不要把开关名写进术语表。

### 文档自洽（温和）

每份文件写清自己职责内的内容，不要用「详见某某」代替本文件该有的步骤、禁令或验收。跨文件链接只指向本文「文档地图」里规定的职责文件，不堆导航。同一含义仍只在一处权威；不要为「禁交叉引用」把术语表抄进 README。

### ADR：原则上只增加

三条同时成立才记：难逆转；没上下文会费解为什么；有真实备选。缺任一就跳过。新决策追加在 `adr.md` 文末。不要一决策一个文件。

已有条目：**明显过期、重复、与新决策冲突**才改。改法三选一，见 [ADR-FORMAT.md](./ADR-FORMAT.md)：冲突到会影响新决策判断 → 删除；过时但仍能提供有效信息 → 挪到 `history.md`；同一条还活着只改细节 → 重写该条并改日期。

### 目标架构先行

多入口 / 多模块 / 对照实验环境：动手写代码之前先有 `architecture.md` 的核心功能、核心模块、暂时或明确不做。多个系统组合**分开**写架构，除非写的是系统之间怎么通信。第一条可跑通路径不是设计终点。目录怎么摆见 Python 仓结构规范（邻域入口：`python-standard-coding` → `references/prd-fastapi.md`）。有 UI 文档时，改界面先读 `DESIGN.md`。

### 最小视图

把项目、模块或代码文件整理成能说清关键点的可视化。`architecture.md` 只用清单和文字；图走本条。要画时 Read [SHOW-FORMAT.md](./SHOW-FORMAT.md)。

**用**：

1. clone 的新项目没有可视化架构图，且用户要看结构 / 画一下 / 了解模块边界。不自动画。已有 `docs/overview.md` 或 `.html` 则先读，避免另画一张互相矛盾。
2. 用户要了解算法、调用链、组件边界、目录职责、数据流、改动差异。
3. 一个英文单词能指代的成熟方案（RAG / SaaS / ERP 等）：按通行结构当场画，不预置模板。

**落盘**（先判要不要写文件）：

- 用户明确指定路径 → 用该路径。
- 场景 1 → 工作区根 `docs/overview.md`。复杂界面、Mermaid 放不下 → `.html`，写完 `Invoke-Item` 打开；`.md` 不打开。
- 用户点名的模块 → `docs/<模块名>-overview.md`（或对应 `.html`）。
- 脚本文件 → 与脚本同级 `<文件主名>.overview.md`。
- 场景 2 当轮解释 → 默认只在对话里；用户说留下或指定路径才写。
- 场景 3 无项目且未指定路径 → 只在对话里，不在工作区建 `docs/`。
- 多包仓 → 默认工作区根的 `docs/`，除非用户指定。
- 目标路径已有文件 → 覆盖。要留旧版走 git。
