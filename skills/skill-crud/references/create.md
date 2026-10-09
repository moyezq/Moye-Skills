# 新建一个 skill

用户说「做个 skill」「把这个流程存成 skill」「新建 skill」时走这一份。

## 1. 抓意图

当前对话里先榨：用户刚做过的工作流、用过的工具、纠正过的步骤、观察到的输入输出格式。再从用户补齐四问：

1. 这个 skill 让 agent 做什么？
2. 什么时候触发——用户会说什么话、处在什么上下文？
3. 产出什么格式？
4. 要不要造测试用例？产出客观可验的（文件变换、数据抽取、代码生成、固定步骤）值得造；文风、设计这类主观产出通常不必。给建议，让用户拍。

**完成标准**：能用一句「领域 + 任务 + 触发说法」说清，四问都有答案。

## 2. 先判值不值得建

按 `SKILL.md` 的第 1 条判据：会重复发生 **且** 模型默认不会做。缺一条就把活当场干了，别建 skill。

## 3. 问边界

主动问边界用例、输入输出样例、成功判据、依赖。这一步问完再写测试 prompt，顺序反了会白写。

**完成标准**：边界用例、样例、依赖都记下来了，没有「大概是这样」这类存疑处。

## 4. 落目录与 frontmatter

建 `skills/<name>/SKILL.md`（`skills/` 是唯一写入落点，各产品目录是它的联接）。

- `name`：kebab-case，与目录同名。命令名就等于这个名字，见 `references/mechanics.md`。
- `description`：写清做什么 + 什么时候用，触发分支全放这里，正文不放。宁可写足：该触发时没触发是常态故障，多写几个触发说法比省字划算。**不要**在 description 里罗列 `references/` 路径——路径写在正文认场景表（见 `references/style.md`「指针怎么写」）。
- 要人打命令触发，就按 `references/mechanics.md` 加 `命令：` 尾巴。

**完成标准**：`python skills/skill-crud/scripts/validate_skill.py skills/<name>` 通过。

## 5. 写正文

先读 `references/style.md`，按它写。每条步骤配完成标准。

## 6. 给对照，等点头

按 `SKILL.md` §4：把「要建这个 skill、`description` 原文、正文骨架」摆给用户，点头再落盘。新建没有「改前」，但「为什么值得建、边界在哪」就是这一轮要过的对照。

**完成标准**：name、description、正文骨架、目录落点都摆过且用户同意。

## 7. 查与收尾

- 跑脚本层：`python skills/skill-crud/scripts/validate_skill.py skills/<name>`。
- 连带文件同轮改完，`skills-list.md` 必加一行。

**完成标准**：脚本通过、连带文件已改。回报按 `references/style.md` 的「改动怎么给人看」写成三行（改前 / 改后 / 为什么）。
