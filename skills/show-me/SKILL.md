---
name: show-me
description: >-
  用最少视觉手段讲清当前话题：伪代码、调用树、组件树、浅层文件树、Mermaid、
  diff 形变、可打开的聚焦 HTML。用户说「画一下 / 示意 / 用图讲 / 结构长什么样 /
  调用关系 / 数据流 / show me / 可视化讲清楚」时用；解释逻辑、UI 结构、重构边界、
  前后差异时优先读本 skill，少写长文。
---

# 可视化讲清（show-me）

用视觉把当前话题讲明白。跳过开场套话，正文短。选**能说清关键点的最小视图**。

## 何时用 / 何时不用

**用**：要把算法、调用链、组件边界、目录职责、数据流、改动差异讲清楚；用户要「看一眼就懂」。

**不用**：要落成可交互分析面板 / 图表仪表时用官方 `canvas`；纯事实查询直接答。

## 视图选型

按问题选一种或几种，**不要全用**，别堆满。

### 逻辑 / 算法 → 伪代码

```text
on(save)
  if content is unchanged
    return cached result
  write new content
  return fresh result
```

### 运行时控制流 → 调用树

```text
submitForm
  createSession
    persistPrompt
    launchAgent
  navigateToSession
```

### UI 结构 → 组件树

带上有关的 state 与模块边界：

```tsx
<SessionPage> (apps/example/src/routes/session.tsx)
  useSessionEvents()
  <SessionToolbar>
    <RunSkillButton> (packages/ui)
```

### 文件职责 / 大重构 → 浅层文件树

```text
src/
├── commands/       # 解析用户动作
├── sessions/       # 拥有 session 状态
└── transport/      # 发 API 请求
```

### 组件交互 / 控制流 / 数据流 → Mermaid

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Daemon
    User->>UI: choose command
    UI->>Daemon: send expanded prompt
    Daemon-->>UI: stream result
```

### 重点是「改了什么」→ diff

周围形状已存在时用 `diff`；diff 形态要贴合话题。

组件改动：

```diff
 <SessionPage>
   useSessionEvents()
   <SessionToolbar>
+    <RunSkillButton />
   <SessionTimeline>
+    <SkillResultCard />
```

目录布局改动：

```diff
 src/
 ├── commands/
+│   └── show-me.ts       # 展开 slash command
 ├── sessions/
-└── transport.ts
+└── transport/
+    ├── client.ts
+    └── stream.ts
```

调用树 / 调用栈改动：

```diff
 submitForm
   createSession
     persistPrompt
+    expandSkillMention
     launchAgent
-  navigateToSession
+  navigateToSession
+    subscribeToEvents
```

状态或控制流改动：

```diff
 on(save)
-  write content
+  if content is unchanged
+    return cached result
+  write new content
+  invalidate cache
```

### 整块都是新形状 → 完整代码块

大半是新内容、省略会藏掉所有权/顺序、或用户需要可复制的目标形状时，给整块：

```ts
function expandSkill(command: string): string {
  const skillName = command.slice(1)
  return `use the ${skillName} skill`
}
```

### 密 UI / 布局 / 状态对比 / Mermaid 放不下 → 聚焦 HTML

写**一个**聚焦 HTML（示意图、信息图、或短幻灯，择一贴合要点）。对齐产品配色、字体、间距与组件；用真实标签与数据；兼顾桌面与移动。然后打开给用户看（Windows）：

```powershell
Invoke-Item "$env:TEMP\show-me-{description}.html"
```

文件名用短英文描述；默认落在 `$env:TEMP`，除非用户指定路径。

## 呈现纪律

* 每个视觉紧挨它支撑的那段短文字。
* 只保留回答当前问题（或解当前分歧的选项）所需的调用、文件、props、state、边界。
* 可用一种，可用几种，几乎不会全用。自行判断，别淹没用户。
