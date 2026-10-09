# 删掉一个 skill

用户说「删掉这个 skill」「这个 skill 不要了」「退役一个 skill」时走这一份。移进 `backup/` 暂存也走这里——它同样要从扫描根里消失。

## 1. 扫引用

枚举着扫会漏：`grep` 一类的工具默认跳过隐藏文件与被 `.gitignore` 排除的目录，而本仓的 `.env.example` 与 `preinstall/` 正好是这两种。实测漏过——`preinstall/SOURCES.md` 里就有活指针。所以用一条全仓兜底扫：

```powershell
Get-ChildItem -Path . -Recurse -File -Force |
  Where-Object { $_.FullName -notmatch '\\\.git\\|\\\.idea\\|\\[^\\]*-workspace\\' } |
  Select-String -Pattern "<skill 名>"
```

`-Force` 是必须的（不加深扫不到隐藏文件与被 `.gitignore` 排除的目录）。排除表里那三样是噪音源：`.git` 是版本库自身，`.idea/` 是编辑器元数据，`*-workspace/` 是临时产出目录——它们都会命中名字，但都不是仓里的引用。

命中的每一行都要归类，四类动作完全不同：

| 类 | 例子 | 动作 |
|---|---|---|
| 活指针 | 别的 skill 里的「→ `<skill 名>`」、`skills-list.md` 的清单行**与那行计数**（「共 N 个」里的 N 是活事实）、`.env.example` 里的注释、脚本里写死的自指字符串、`preinstall/SOURCES.md` 的**去向列** | 改指向新落点，或整行删 |
| 决策记载 | `docs/adr.md` 里「X 已并进 Y」 | 留着，一个字不动 |
| 别人的事实 | `analyse/` 里指上游同名 skill 的段落、`.idea/` 这类编辑器本地状态 | 留着 |
| 暂存与取源记载 | `skills-list.md` 的「暂存（不进工作树）」清单行、`preinstall/SOURCES.md` 里「这个 skill 从哪个上游来的」那几列 | 留着：落点仍存在（`backup/` 或上游），改掉反而抹掉归属 |

一句话分辨：**落点还在的记载留着，落点没了的那一半才是活指针**。`preinstall/SOURCES.md` 一行里两者并存——去向列是活指针（要改成新落点），上游仓库名是记载（一个字别动）。

被删目录**内部**的自指（`SKILL.md` 的 `name:`、脚本里写自己的名字、正文里的同目录路径）不列进清指针清单：它们随目录一起消失。但要确认其中的行为有没有替身——脚本写死的自指字符串若已在保留文件里改过名，行为不丢；没改就先把替身补上。

顺带核实产品目录：`~\.dsh\skills`、`~\.cursor\skills`、`~\.agents\skills` 是指向本仓 `skills/` 的联接。删仓内目录即三端同时消失，**不要**去产品目录删——那会把联接本身拆掉。

**完成标准**：每条命中都归了类，零命中的位置也逐个点名报出（列出来是为了复验时有对照），或明确报告「零引用」。

## 2. 报清单等人点头

给用户三样：要删（或要移走）的目录、引用清单（文件 + 行号）、每条引用准备怎么改（删掉还是改成指向谁）。这是写盘动作，拿到明确同意再进下一步。

## 3. 删与清

删目录（或移进 `backup/`），同轮把上一步列的引用逐条改掉或删掉。

## 4. 复验

把第 1 步的扫描**收窄成活指针范围**再跑一次，逐条对着第 2 步的清单核：

```powershell
Get-ChildItem -Path skills,preinstall -Recurse -File -Force |
  Where-Object { $_.FullName -notmatch '<待删目录1>|<待删目录2>' } |
  Select-String -Pattern "<skill 名>"
Select-String -Path CONTEXT.md,skills-list.md,README.md,.env.example -Pattern "<skill 名>"
```

判据写成两半：活指针 删前 N 条 → 删后 **0** 条；记载类（`docs/adr.md`、`analyse/`、`*-workspace/`）删前条数 = 删后条数。

为什么复验要收窄口径：`docs/adr.md` 的合并记载、`analyse/` 里指上游同名 skill 的段落本来就该留下。按全仓裸名字判零会让这条判据永远假红，下一轮就没人信它了。

**完成标准**：活指针真的归零，记载类一条不多一条不少，且清单里每条都指着落盘后的实际状态。

## 5. 记录

决策性删除（合并、退役）在 `docs/adr.md` 补一条：谁并进谁、为什么、否掉的备选是什么。git 提交等用户说「同步」再动。
