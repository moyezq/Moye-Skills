---
name: self-python-style
description: 写或改 Python 文件时查阅本机代码风格（docstring、行内注释、文件内顺序、命名、信任上游字段、运行参数、print 与 logger）。业务启动与 README 命令分两步：conda activate 环境，再 python / pip；禁止 conda run -n。本对话第一次为任务跑 Python 时做 conda 日探测（探测脚本不算）；缺包不预检、失败再报告。新项目装环境依赖时钉 requirements.txt（包名==版本），只装能跑起来的最小集。切步与入口脚本顶部注释见 self-python-script；函数抽法与 FastAPI 见 self-python-function；目录见 self-python-project。命令：/self-python-style
---

# Python 代码风格与怎么跑

管 **本机 Python 看起来什么样、第一次怎么跑**。怎么抽函数、流水线类内部、FastAPI 路由见 `self-python-function`。分阶段脚本怎么切步、入口脚本文件头怎么分层见 `self-python-script`。

完成标准：写到的每个 def 都有本文件规定的 docstring；重要块有 `#` 说明；文件内顺序符合「辅助在上、入口在下」；命名用常见英文单词 + 下划线 / 数字；字段按上游约定直接取；运行参数写成常量赋值；脚本与探测入口用 `print`，FastAPI 生产用项目已有 logger。第一次为任务跑 Python 时：环境卡 conda 字段已按日探测或沿用；缺包不预检。新项目装依赖结束时：项目根 `requirements.txt` 每一行都是这次直接装的包，格式 `包名==版本`。

## 何时用

**用**：写或改 `.py`；或本对话第一次要为任务跑 Python；新项目装环境依赖。

**不用**：探测脚本（`env_detect.py` / `conda_envs.py`）不算为任务跑 Python。只改目录、不改 Python 正文。

---

## 1. 跑 Python：conda 环境与缺包

默认环境 **base**；用户或项目 README 点名了才换（如 `rag`）。会话索引根目录定位见 `self-session-bootstrap`（本 skill 不要写死盘符）。环境卡：`<会话索引根>/scripts/_meta/env_card.json`。对照对话里的今天，写成 `YYYY-MM-DD` 再和 `conda_date` 比。

第一次为任务跑 Python 时（探测脚本不算）：

1. Read 环境卡（没有当过期）。`conda_date` 等于今天则用卡里的 `conda_envs`。
2. 否则（这不是为任务跑 Python，探测仍用 `conda run`）：

```powershell
conda run -n base python "<会话索引根>/scripts/conda_envs.py"
```

当天 `conda_date` 已是今天则不要再跑。不要跑 `pip list`。

3. 业务入口、README、告诉用户怎么跑：**禁止** `conda run -n`。每个终端两步：

```powershell
conda activate <环境>
python <入口>
```

装包只走已 activate 的环境的 `pip`，不信 PATH 上未激活的 `pip`。

不预检第三方包。出现 `ModuleNotFoundError` / `ImportError` 时不要自己装，向用户报告：

- 当前环境名
- 这次运行的入口（脚本路径或等价入口）
- 缺的包名
- 简短报错日志
- 准确安装命令（同样两步，不要 `conda run`）：

```powershell
conda activate <环境>
pip install <包>
```

用户说装再执行该安装命令。对齐阶段说「用某 conda 环境测、允许多装一个包」视为已授权安装该包，不必再问一次。

**新项目装依赖**：用户让给新项目装环境依赖时，只装运行入口真正需要的第三方包（代码 `import` 或启动命令直接用到；标准库能覆盖的不装）。装完先 `conda activate <环境>`，再用 `pip show <包>` 读发行名与 Version，写入项目根 `requirements.txt`，每行 `包名==版本`。文件只记这些直接依赖。

---

## 2. Docstring 与行内注释

每个方法都有 docstring。保留原有注释见兜底原则「外科式改动」。

**对外方法**（工具函数、类的公开方法、utils、脚本里的 `stepN_xxx`）写：功能、应用场景、输入、输出；有约定时加异常。

```python
def load_sample_data(path: str) -> list:
    """
    从样例 JSON 加载指定日期的新闻列表。

    功能：读取本地 fixture，按 create_date 过滤。
    应用场景：离线流水线步骤 1，替代数据库查询。
    输入：path — 样例 JSON 路径。
    输出：dict 列表；无匹配日期时返回 []。
    异常：文件不存在 → FileNotFoundError。
    """
```

**工具集文件** — 模块 docstring 顶部集中写「使用前注意事项」（依赖、缓存文件、Windows 路径、通用异常行为）；各方法不重复。

**入口脚本 / utils** — 模块 docstring 列出职责、步骤编号、产出路径、对外函数清单。入口脚本怎么把这些字段嵌进「一句开场 / 原理 / 例子 / 怎么跑」、以及原理编号与入口编号为何要分开，见 `self-python-script` 的「顶部注释」。

私有 `_` 辅助也要有 docstring，可一行。

方法里按块或重要行加 `#`，写这小段在做什么。踩坑备注留在用到的那一行旁边，不写到文件头当散文。

## 3. 文件内顺序

辅助与内部实现在上，越靠近对外入口越往下，入口方法在文件下部。`if __name__ == "__main__":` 放在文件最末尾。

可单独试的模块（例如一个模型 API 的调用函数）在 `__main__` 里写简单调研例子：硬编码最少参数，打一次调用并 `print` 结果。不要在 `__main__` 里写完整业务。

分阶段脚本的 `stepN` 仍按执行序号从上到下排，`__main__` 仍在最末尾；切步规则见 `self-python-script`。

## 4. 命名

文件名、函数名、变量名用常见英文单词，单词之间下划线，序号用数字（`step2_fetch_detail`、`user_id`）。不要靠缩写堆砌（`usr_repo`、`typ_b`）。

类名用 PascalCase，仍由常见单词组成（`UserRepository`）。含中文的 `.py` 文件头加 `# -*- coding: utf-8 -*-`。

## 5. 信任上游字段

实现前先明确：谁在调用、输入从哪来、输出给谁。按上游已约定的字段名与结构直接访问。

格式不确定时查调用方、样例 JSON 或 docstring，再写访问代码。不要在函数里用多重 `isinstance` / `get(..., default)` 去猜未知形状。

## 6. 运行参数

运行参数写成文件顶部常量，或 `__main__` 里的赋值。分阶段脚本里常量区怎么摆见 `self-python-script`。

不用 `argparse`、`sys.argv`、click。

## 7. print 与 logger

案例脚本、分阶段入口、可探测模块的 `__main__` 用 `print`。分阶段前缀（`[阶段N]`、循环进度）见 `self-python-script`。

FastAPI 生产服务用项目已有 logger，不新造一套 logging 配置。
