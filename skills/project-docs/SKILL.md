---
name: project-docs
description: 项目文档。管仓库里 CONTEXT、adr.md、HISTORY.md、architecture、README、AGENTS.md 等什么时候读、什么时候改、什么时候必须照做。讨论术语、写目标态蓝图、定本仓给 AI 的规矩、改启动方式或 UI 规范时用。最小视图：把项目、模块或代码文件收成能说清关键点的可视化；clone 无架构图要看结构、用户要了解算法/调用链/组件边界/目录职责/数据流/改动差异、或一个英文单词指代的成熟方案（RAG/SaaS/ERP）时用。画一下、示意、用图讲、调用关系、数据流、show me、可视化讲清楚走本 skill。写代码若改了叫法、决策、模块状态、端口入口或本仓禁令，同一轮改对应文件，不要攒到下轮。触发词：项目文档、CONTEXT.md、ADR、architecture.md、目标态、模块落点、术语、最小视图。不是 笔记库。配套 grill-with-docs。不要一决策一个 ADR 文件。可交互分析面板走官方 canvas。命令：/project-docs
---

# 项目文档

管仓库里给人、给 AI 看的文档：**什么时候建、读、改、必须照做**。术语一结晶就写下叫法；难逆转决策记 ADR；多模块项目动手前先画目标态；现状用最小视图讲清。

仅仅「读 CONTEXT.md 查词」不是本 skill；本 skill 管的是**改文档并让代码遵守它**，以及用最小视图讲清现状。

## 何时用 / 何时不用

**用**：讨论术语；写或编辑下面「文档地图」里的任何文件；多入口 / 多模块 / 对照实验台动手前画目标态。项目里已有这些文件之一，且本轮代码改了叫法、为什么、模块状态、启动方式、本仓 AI 禁令或 UI 规范。最小视图见下节。

**不用**：只读词、查定义；笔记库（见 `self-notes-read`）；把开发经历抽成面试题（见 `interview-from-dev`）；本轮只改函数内部，且不改叫法、决策、模块落点、端口或入口（缺空检查、修打印）。单文件脚本不必建蓝图和 UI 文档。可交互分析面板 / 图表仪表走官方 `canvas`。

完成标准：本轮若改了某份文档所管的事，对应文件在同一轮已改。不把「下轮规范再改文档」当成完成。每份已存在的文档都按 [DOC-MAP.md](./DOC-MAP.md) 的读 / 改 / 守来用。本轮若画了最小视图：已按 [SHOW-FORMAT.md](./SHOW-FORMAT.md) 选型；该落盘的已写到规定路径；图没有写进 `architecture.md`。

## 文档地图（先看这张表）

宁缺毋滥，按需懒建。不要按清单一次建齐。产品目标与「绝对不做」写进 `docs/architecture.md`，不要另建 `PROJECT-SPEC.md`。蓝图文件名用 `docs/architecture.md`，不要再写一份 `ARCHITECTURE.md`。

每份的建 / 读 / 改 / 守见 [DOC-MAP.md](./DOC-MAP.md)。格式见旁路文件。

| 文件 | 只收什么 | 何时建 |
|------|----------|--------|
| `CONTEXT.md` | 叫法 | 第一个术语结晶 |
| `docs/adr.md` | 现行为什么 | 第一条够格的决策 |
| `docs/HISTORY.md` | 被取代或废弃的改动 | 第一次废决策 |
| `docs/architecture.md` | 目标态：模块、流向、落点、状态、明确不做（清单和文字，不内嵌图） | 多入口 / 多模块 / 对照实验台，动手写代码之前 |
| `docs/overview.md` | 最小视图：现状可视化 | clone 无图且用户要看结构时；密 UI 用 `.html` |
| `README.md` | 给人跑：名称、启动、依赖、结构、使用说明 | 第一条可跑闭环之后，或用户要使用指南 |
| `AGENTS.md` | 本仓给 AI 的例外与禁令 | 全局 skill 管不到的本仓硬规矩出现时 |
| `DESIGN.md` | 配色、间距、基础交互 | UI 超过薄问答页，或用户要定视觉规范 |
| `TODO.md` | 实现勾选清单（蓝图的工作副本） | 目标态蓝图已有之后 |
| `docs/COMPONENT-GUIDELINES.md` | 共享组件规矩 | 有一套真正复用的组件 |
| `docs/PAGE-STRUCTURE.md` | 多页结构与路由 | 多于一页 |
| `docs/DEPLOYMENT.md` | 打包上线 | 真要发布时 |

改叫法改 `CONTEXT.md`。改仍有效的为什么则重写或追加 `docs/adr.md`。废掉一条决策则删 `adr.md` 对应条并追加 `HISTORY.md`。改模块边界或状态改 `architecture.md`。改怎么跑改 `README.md`。改本仓 AI 禁令改 `AGENTS.md`。现状怎么长用最小视图，不要画进蓝图。

## 文件结构

按需出现，不是每个仓库都有全套：

```
/
├── AGENTS.md
├── README.md
├── CONTEXT.md
├── DESIGN.md
├── TODO.md
└── docs/
    ├── architecture.md
    ├── overview.md
    ├── adr.md
    ├── HISTORY.md
    ├── COMPONENT-GUIDELINES.md
    ├── PAGE-STRUCTURE.md
    └── DEPLOYMENT.md
```

根目录存在 `CONTEXT-MAP.md` 表示多上下文。格式：[CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md)、[ADR-FORMAT.md](./ADR-FORMAT.md)、[ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md)。最小视图选型：[SHOW-FORMAT.md](./SHOW-FORMAT.md)。

## 会话中怎么做

### 对照术语表挑战

用户用的词和 `CONTEXT.md` 冲突时立刻指出：「术语表把 X 定义为 …，但这里像在指 Y，是哪一个？」

### 打磨模糊用词

一词多义时给出规范词：「account 是 Customer 还是 User？这是两个东西。」

### 用具体场景压测

发明探边界的场景，逼概念边界说精确。

### 与代码交叉核对

用户说「某功能是这样」时，对代码。本轮把蓝图「未做」做成了「已实现」，同一轮改状态标记。

### 就地更新 CONTEXT.md

术语一解决就更新，不要攒批。`CONTEXT.md` 只收叫法：代码变了若**定义**过时，改定义，不要把开关名写进术语表。

### 谨慎给 ADR

三条同时成立才记：难逆转；没上下文会费解为什么；有真实备选。缺任一就跳过。同一条决策改了细节：重写 `adr.md` 里那条并改日期，不要只打现状补丁。整条被取代或废弃：从 `adr.md` 删掉，追加 `HISTORY.md`。否定旧选定的那一轮，完成标准见 [ADR-FORMAT.md](./ADR-FORMAT.md)：旧条已处理、蓝图已改、AGENTS 有引用也已改。

### 目标态先行

多入口 / 多模块 / 对照实验台：动手写代码之前先有 `architecture.md` 的目标模块与目录落点。第一闭环不是设计终点。目录怎么摆见 `self-python-project`。有 UI 文档时，改界面先读 `DESIGN.md`，见 `self-frontend`。

### 最小视图

把项目、模块或代码文件收成能说清关键点的可视化。蓝图（`architecture.md`）只用清单和文字；图走本条。要画时 Read [SHOW-FORMAT.md](./SHOW-FORMAT.md)。

**用**：

1. clone 的新项目没有可视化架构图，且用户要看结构 / 画一下 / 了解模块边界。不自动画。已有 `docs/overview.md` 或 `.html` 则先读，避免另画一张打架。
2. 用户要了解算法、调用链、组件边界、目录职责、数据流、改动差异。
3. 一个英文单词能指代的成熟方案（RAG / SaaS / ERP 等）：按通行结构当场画，不预置模板。

**落盘**（先判要不要写文件）：

- 用户明确指定路径 → 用该路径。
- 场景 1 → 工作区根 `docs/overview.md`。密 UI、Mermaid 放不下 → `.html`，写完 `Invoke-Item` 打开；`.md` 不打开。
- 用户点名的模块 → `docs/<模块名>-overview.md`（或对应 `.html`）。
- 脚本文件 → 与脚本同级 `<stem>.overview.md`。
- 场景 2 当轮解释 → 默认只在对话里；用户说留下或指定路径才写。
- 场景 3 无项目且未指定路径 → 只在对话里，不在工作区建 `docs/`。
- 多包仓 → 默认工作区根的 `docs/`，除非用户指定。
- 目标路径已有文件 → 覆盖。要留旧版走 git。
