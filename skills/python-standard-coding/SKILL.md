---
name: python-standard-coding
description: >-
  Python 写法与落盘的中文规范：风格与怎么跑、类型标注、函数签名与重构、容器选择、
  大输入与性能、单文件脚本、多文件目录与 README。写或改 .py、写脚本、抽函数或拆文件、
  补类型标注、改返回值形状、重构一段代码、新建或整理 Python 仓目录时查阅。
---

# Python 写法与落盘

管 **Python 怎么写、怎么跑、脚本怎么切、函数怎么抽、类型怎么标、容器怎么选、多文件项目文件放哪**。

## 何时用

**用**：写或改 `.py`；第一次为任务跑 Python；新项目装依赖；写单文件脚本或入口文件头；改函数/类/FastAPI 路由或嫌拆太碎；补类型标注或改返回值形状；重构一段已有代码；新建/整理 Python 项目目录或写改根 README。

**不用**：探测脚本（`env_detect.py` / `conda_envs.py`）不算为任务跑 Python。pytest 定缝与用例见 `self-python-testing`。只改 ADR / architecture / 术语表、不动代码与目录树。前端页面、桌面壳、知识库笔记。

## 技能清单

| 任务 | 读 |
|------|-----|
| 风格、conda、缺包、requirements、docstring、命名、文件内顺序、常量、`__all__`、print/logger | 下文「全局规范」 |
| 异常：`except` 怎么写、谁兜底、换异常类型 | [references/exceptions.md](./references/exceptions.md) |
| 类型标注：`-> None`、`Iterable`/`Sequence`、默认参数、`Protocol`、`TypedDict`、`Final` | [references/typing.md](./references/typing.md) |
| 抽函数/拆文件、参数与返回值怎么写、重构后确认行为没变、提前 return、嵌套与参数个数上限、路由函数与数据模型 | [references/function.md](./references/function.md)（F1–F9 + H1–H7） |
| 容器选择：`set` / `Counter` / `defaultdict` / `deque` / 路径 | [references/containers.md](./references/containers.md) |
| 边界数据校验（pydantic / `dataclass` 的分工） | [references/function.md](./references/function.md) F9 |
| 大文件、大结果集流式处理、比内存大的数组 | [references/perf.md](./references/perf.md)（P1、P4） |
| 单文件脚本、stepN、入口文件头、`data/`、运行上限 | [references/script.md](./references/script.md) |
| 多文件目录、README、FastAPI、前后端同仓 | [references/project.md](./references/project.md) |

完成标准：命中「按任务读哪一块」的每一块，该块要求都做到。

带「何时读」的 reference 只在条件满足时读。

---

## 全局规范

### S1 跑 Python：先 `conda activate`，再 `python`

- 每个终端两行，一行管环境、一行管运行；不用 `conda run -n`

```text
# ✅ 正确
conda activate base
python main.py

# ❌ 错误
conda run -n base python main.py
```

- AI 自己在非交互 shell 里跑时不依赖 `conda activate`：用解释器绝对路径 `<envs>/<环境>/python.exe -m pytest …`
- 装包走已激活环境里的 `pip`，不信 PATH 上那个

### S2 缺包报告给用户，不自己装

- 直接 `import`，缺了把五项报给用户；不预检第三方包、不自动 `pip install`

```python
# ✅ 正确
import pandas          # ModuleNotFoundError → 报环境名 / 入口 / 包名 / 报错 / 安装命令

# ❌ 错误
if importlib.util.find_spec("pandas") is None:
    subprocess.run(["pip", "install", "pandas"])
```

```powershell
conda activate <环境>
pip install <包>
```

- 用户说装再执行；对齐阶段说过「允许多装某包」的视为已授权
- 不跑 `pip list` 探测

### S3 `requirements.txt` 只写直接依赖

- 只写运行入口真正 `import` 到的第三方包，每行 `包名==版本`；不抄 `pip freeze` 的全部结果

```text
# ✅ 正确
numpy==2.1.0
pandas==2.2.2

# ❌ 错误
numpy==2.1.0
pytz==2024.1        # numpy 拉的
six==1.16.0
```

- 标准库能覆盖的不装；装完用 `pip show <包>` 读发行名与 Version 写进去

### S4 docstring：每个方法都写，对外方法写清五件事

- 对外方法（工具函数、类的公开方法、`utils`、脚本里的 `stepN_xxx`）的 docstring 写清五件事：做什么、什么时候能用、吃什么、吐什么、什么时候报错

```python
# ✅ 正确
def load_sample_data(path: str) -> list:
    """
    从样例 JSON 加载指定日期的新闻列表。
    功能：读取本地 fixture，按 create_date 过滤。
    应用场景：离线流水线步骤 1，替代数据库查询；不接生产数据源。
    输入：path — 样例 JSON 路径。
    输出：dict 列表；无匹配日期时返回 []。
    异常：文件不存在 → FileNotFoundError。
    """

# ❌ 错误
def load_sample_data(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return [x for x in json.load(f) if x["create_date"] == "2024-01-01"]
```

- 私有 `_` 函数写一行即可，可以只有一句用途，判据是「函数名 + 签名 + 函数体都推不出来的信息」
- 有分支、有边界处理、有副作用、有非默认参数、或有「哪些异常会被吞」这类契约时，必须写清那一句
- 一律不复述函数名、不复述签名、不复述函数体

```python
# ✅ 正确
def _norm(s: str) -> str:
    """去掉首尾空白并按 NFC 归一化，用于跨源比对。"""

# ❌ 错误
def _norm(s: str) -> str:
    """归一化字符串。"""
def _load(path, encoding="utf-8"):
    """_load(path, encoding) -> dict"""
def _total(items: list) -> int:
    """遍历 items，把每项的 price 加起来返回。"""
```

### S5 对整个文件成立的前提写在模块 docstring；行内注释写在用到的那一行

- 工具集文件把「使用前注意事项」集中写在模块 docstring：依赖、缓存文件、Windows 路径、通用异常行为
- 入口脚本 / utils 的模块 docstring 列职责、步骤编号、产出路径、对外函数清单

```python
# ✅ 正确
"""图像工具集。
使用前注意事项（对全部方法生效）：依赖 PIL；结果缓存于 data/cache.json。
对外函数：resize / crop / to_thumbnail。"""

def crop() -> None:
    """居中裁剪为正方形。"""

# ❌ 错误
def resize() -> None:
    """注意：结果缓存在 data/cache.json。"""
def crop() -> None:
    """注意：结果缓存在 data/cache.json。"""
```

- 行内 `#` 写这一小段在做什么；踩坑备注留在用到的那一行旁边，不写成文件头的散文

### S6 小函数在上、入口在下，`__main__` 放最末尾

- 被调用的函数与内部实现在上，越靠近对外入口越往下；`if __name__ == "__main__":` 放文件最末尾

```python
# ✅ 正确
def _load() -> dict: ...
def _clean(raw: dict) -> dict: ...

def main() -> None:
    _clean(_load())

if __name__ == "__main__":
    main()

# ❌ 错误
def main() -> dict:
    return _load()
if __name__ == "__main__":
    main()
def _load() -> dict: ...
```

- 分阶段脚本的 `stepN` 按执行序号从上到下排

### S7 可单独试的模块，`__main__` 里留个最小调研例子

- `__main__` 是这个文件的自测开关，不是业务入口：硬编码最少参数，打一次调用并打印结果
- 完整业务流程留给入口脚本或服务启动文件

```python
# ✅ 正确
if __name__ == "__main__":
    print(parse_record({"id": 1, "text": "测试文本"}))

# ❌ 错误
if __name__ == "__main__":
    for row in db.query("select * from orders"):
        process(row)
```

### S8 名字用常见英文单词拼，不堆缩写

- 文件名、函数名、变量名：常见英文单词，单词之间下划线，序号用数字
- 类名 PascalCase，仍由常见单词组成
- 不用缩写堆砌

```python
# ✅ 正确
def get_user_repository(user_id: int, repo_type: str) -> str: ...
def step2_fetch_detail(api_host: str, path_word: str) -> dict: ...
class UserRepository: ...

# ❌ 错误
def get_usr_repo(uid, typ_b): ...
def calc_tot_amt(amt_lst): ...
class usr_repo: ...
```

### S9 探针与工具脚本加名字前缀，不占标准库的模块名

- 探针、临时工具脚本的文件名加业务前缀（`<前缀>_probe_<用途>.py`、`<前缀>_tool_<用途>.py`），不占用标准库的模块名

```python
# ✅ 正确
# dsh_probe_inspect.py    dsh_tool_typing_report.py

# ❌ 错误
# inspect.py    typing.py    json.py
```

### S10 模块常量集中置顶

- 模块常量放 import 之后、函数之前，名字全大写、单词之间下划线；不在函数体里定义常量
- 同一个值只在这一个地方出现

```python
# ✅ 正确
MAX_PAGE_SIZE = 20
DEFAULT_TIMEOUT_SEC = 30.0

def fetch_page(n: int) -> list:
    if n > MAX_PAGE_SIZE:
        n = MAX_PAGE_SIZE
    ...

# ❌ 错误
def fetch_page(n: int) -> list:
    if n > 20:
        n = 20
    ...

def fetch_all(items: list) -> list:
    for chunk in chunks(items, 20):
        ...
```

### S11 循环里拼字符串先收集再 `join`，不用 `+=` 累加

- 片段先攒起来，最后一次 `分隔符.join(...)` 合成；不在循环里 `out += ...`

```python
# ✅ 正确
out = ", ".join(str(item) for item in items)
out = "\n".join(format_line(row) for row in rows)

# ❌ 错误
out = ""
for item in items:
    out += str(item) + ", "
```

### S12 运行参数写成文件顶部常量，不用 argparse

- 运行参数写成文件顶部常量，临时调整写在 `__main__` 第一行；不用 `argparse`、`sys.argv`、`click`
- 参数来自外部、要被别人长期调用的程序才做命令行参数

```python
# ✅ 正确
COMIC_NAME = "书名"
LIMIT = 10

if __name__ == "__main__":
    COMIC_NAME = "临时换一本"

# ❌ 错误
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--comic", required=True)
parser.add_argument("--limit", type=int, default=10)
args = parser.parse_args()
COMIC_NAME, LIMIT = args.comic, args.limit
```

### S13 脚本用 `print`，服务用项目已有的 logger

- 脚本的输出终点是终端：用 `print`，前缀自带阶段号
- 生产服务的输出终点是日志采集系统：用项目已有的 logger，不新造 logging 配置

```python
# ✅ 正确
print("[阶段2] 已写入 data/result/step2_detail.json")   # 脚本
logger.warning("处理订单 %s 失败", order_id)             # 服务

# ❌ 错误
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.info("[阶段2] 已写入 data/result/step2_detail.json")   # 脚本里配了一整套 logging
print(f"处理订单 {order_id} 失败")                             # 服务里绕过项目日志配置
```

### S14 文件读写显式 UTF-8；中文输出先设 `PYTHONUTF8=1`

- 文件读写一律写死 `encoding="utf-8"`
- 命令行跑、输出有中文时先设 `PYTHONUTF8=1`，或在脚本里 `sys.stdout.reconfigure(encoding="utf-8")`
- 不写 `# -*- coding: utf-8 -*-` 编码声明

```python
# ✅ 正确
open("out.json", "w", encoding="utf-8").write("中文")
sys.stdout.reconfigure(encoding="utf-8")

# ❌ 错误
open("out.json", "w").write("中文")
# -*- coding: utf-8 -*-        # Python 3 下不做任何事
```

```powershell
$env:PYTHONUTF8=1
python x.py
```

- 要把输出落成文件核对，用 `cmd /c "python x.py > x.bin"`（字节直通）或 Python 自己写；不用 PowerShell 管道配 `Out-File -Encoding utf8`——解不出的字节会变成 U+FFFD 写进文件，从此不可还原

### S15 用 `with` 管资源

- 打开文件、套接字、临时目录一律用 `with`
- FastAPI 里进程级连接放项目已有的 lifespan

```python
# ✅ 正确
with open("data.txt", encoding="utf-8") as f:
    content = f.read()

# ✅ 正确 —— 多个资源一次管住
with open("in.txt", encoding="utf-8") as src, open("out.txt", "w", encoding="utf-8") as dst:
    dst.write(src.read())

# ❌ 错误
f = open(path, encoding="utf-8")
content = f.read()
if not content:
    return []                # 提前返回，f 永远不关
f.close()
```

### S16 两个模块互相 import：两种写法按「运行期用不用它」选

- 运行期真要用的名字：延迟到函数内部 import
- 只在类型标注里用的名字：放进 `if TYPE_CHECKING:` 块

```python
# ✅ 正确 —— 运行期要用的
def get_service():
    from mypackage.services import UserService
    return UserService()

# ✅ 正确 —— 只有类型标注用的
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypackage.models import User

def save(user: User) -> None: ...

# ❌ 错误 —— a.py 与 b.py 顶部互相 import，结果取决于谁先被导入
# a.py:  from b import make_b
# b.py:  from a import make_a
```

### S17 有对外接口的模块显式写 `__all__`

- 只列对外承诺的名字
- 位置：模块 docstring 之后、任何 import 之前（`from __future__` 除外）
- 入口脚本、`__main__` 文件、没有对外接口的工具集不写

```python
# ✅ 正确
"""订单加载与校验。"""

__all__ = ["load_records", "RecordError"]

from pathlib import Path

def load_records(path: Path) -> list: ...
def _helper() -> None: ...

# ❌ 错误 —— import * 会把 json、Path 一起带出去
import json
from pathlib import Path

def load_records(path: Path) -> list: ...
```
