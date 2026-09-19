---
name: self-python-style
description: 写或改 Python 文件时查阅本机代码风格（docstring、行内注释、文件内顺序、命名、信任上游字段、运行参数、print 与 logger）。本对话第一次为任务跑 Python 时做 conda 日探测（探测脚本不算）；缺包不预检、失败再报告。切步见 self-python-script；函数抽法与 FastAPI 见 self-python-function；目录见 self-python-project。
---

# Python 代码风格与怎么跑

管 **本机 Python 看起来什么样、第一次怎么跑**。怎么抽函数、流水线类内部、FastAPI 路由见 `self-python-function`。分阶段脚本怎么切步见 `self-python-script`。

完成标准：写到的每个 def 都有本文件规定的 docstring；重要块有 `#` 说明；文件内顺序符合「辅助在上、入口在下」；命名用常见英文单词 + 下划线 / 数字；字段按上游约定直接取；运行参数写成常量赋值；脚本与探测入口用 `print`，FastAPI 生产用项目已有 logger。第一次为任务跑 Python 时：环境卡 conda 字段已按日探测或沿用；缺包不预检。

## 何时用

**用**：写或改 `.py`；或本对话第一次要为任务跑 Python。

**不用**：探测脚本（`env_detect.py` / `conda_envs.py`）不算为任务跑 Python。只改目录、不改 Python 正文。

---

## 1. 跑 Python：conda 环境与缺包

默认环境 **base**；用户点名了才换。装包只走选定环境的 pip，不信 PATH 上的 `pip`。

会话索引根目录定位见 `self-session-bootstrap`（本 skill 不要写死盘符）。环境卡：`<会话索引根>/scripts/_meta/env_card.json`。对照对话里的今天，写成 `YYYY-MM-DD` 再和 `conda_date` 比。

第一次为任务跑 Python 时（探测脚本不算）：

1. Read 环境卡（没有当过期）。`conda_date` 等于今天则用卡里的 `conda_envs`。
2. 否则：

```powershell
conda run -n base python "<会话索引根>/scripts/conda_envs.py"
```

这不是为任务跑 Python。当天 `conda_date` 已是今天则不要再跑。不要跑 `pip list`。

3. `conda run -n <环境> python ...` 跑这次入口。

不预检第三方包。出现 `ModuleNotFoundError` / `ImportError` 时不要自己装，向用户报告：

- 当前环境名
- 这次运行的入口（脚本路径或等价入口）
- 缺的包名
- 简短报错日志
- 准确安装命令：`conda run -n <环境> pip install <包>`

用户说装再执行该安装命令。

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

**入口脚本 / utils** — 模块 docstring 列出职责、步骤编号、产出路径、对外函数清单。

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
