# 函数签名与参数

命中「抽函数、拆文件、参数与返回值怎么写、重构后确认行为没变、提前 return、嵌套与参数个数」时读本文。风格与怎么跑见 [SKILL.md](../SKILL.md)；类型标注见 [typing.md](./typing.md)。

### F1 位置参数不超过 3 个；更多要么放 `*` 之后，要么收成一个参数对象

- 参数多到读不出哪个是哪个时（3 个附近），收成一个有名字的参数对象，或让多出来的走关键字
- 调用点从「必须跳回定义数位置」变成「看名字就知道传的是什么」

```python
# ✅ 正确
from dataclasses import dataclass

@dataclass
class ExportOptions:
    page: int = 1
    overwrite: bool = False
    limit: int = 5000

def export_report(pid: int, options: ExportOptions) -> str:
    ...

export_report(27, ExportOptions(page=3, limit=5000))

# ❌ 错误 —— 五个位置参数：3 是页码还是重试次数？两个 int 写反也不报错
def export_bad(pid: int, page: int, overwrite: bool, limit: int, fmt: str) -> str:
    ...

export_bad(27, 3, True, 5000, "csv")
```

- 3 这个数字是约定不是硬道理；要防的是「两个同类型参数写反、检查器一声不响」

### F2 可选参数放 `*` 之后，只能按名字传

- 可选参数放 `*` 之后：按位置传直接 `TypeError`，错误在编辑期就暴露
- 可选参数天然是配置项，不是数据流的一部分

```python
# ✅ 正确
def shrink(path: str, *, ratio: float = 1.0, inplace: bool = False) -> str:
    ...

shrink("a.txt", ratio=0.8)
shrink("a.txt", 0.8)          # TypeError：`*` 之后不给按位置传

# ❌ 错误 —— True 被当成 ratio；bool 是 int 子类，不报错，只是缩放比变成 1.0
def shrink(path: str, ratio: float = 1.0, inplace: bool = False) -> str:
    ...

shrink("a.txt", True)         # 你以为在传 inplace
```

### F3 只允许几个固定取值的地方，把取值写进类型

- 字符串取值写进签名：`Literal["sync", "async"]`；要跨文件复用或挂方法时升成 `Enum`
- 合法值不写在注释或 docstring 里——`mode == "asnyc"` 永远为假，不报错、测试也过

```python
# ✅ 正确
from enum import StrEnum
from typing import Literal

def convert(src: str, mode: Literal["sync", "async"]) -> str:
    ...

class Mode(StrEnum):            # 取值还要参与逻辑或跨文件复用
    SYNC = "sync"
    ASYNC = "async"

convert("x", "asnyc")           # 检查器当场报错

# ❌ 错误 —— 合法值只活在文档里
def convert(src: str, mode: str) -> str:
    """mode 只能是 'sync' 或 'async'"""
    ...
```

- 只在一处用、不参与逻辑的取值，`Literal` 就够

### F4 不用 `**kwargs` 把参数转手传下去（装饰器的 `(*args, **kwargs)` 除外）

- 包装函数把参数逐个具名列出来再转发，不写成 `def f(**kwargs)`
- 选项以后还会加，用 F1 的参数对象，别用 `**kwargs`

```python
# ✅ 正确
def fetch(url: str, *, timeout: float = 5.0, retries: int = 0) -> str:
    return Client().request(url, timeout=timeout, retries=retries)

fetch(ur1="http://x")          # 立刻 TypeError：参数名错了

# ❌ 错误 —— 签名被抹平，补全、跳转、类型检查、报错位置全丢
def fetch(**kwargs) -> str:
    return Client().request(**kwargs)

fetch(ur1="http://x")          # 不报错，一路传到深处才炸
```

- `retires=3` 这类拼错会静默让重试次数停在 0，请求照发

### F5 一个函数只返回一种形状，签名与实现一致

- 签名写什么就返回什么；空态、失败态显式编码进返回值，不用 `None` / `[]` / `dict` 混着来
- 调用方只需一套解构写法；`if not result` 会把「没查到」和「出错了」折叠成一个分支

```python
# ✅ 正确
from dataclasses import dataclass

@dataclass(frozen=True)
class LoadResult:
    items: tuple[str, ...] = ()
    ok: bool = False

def load(name: str) -> LoadResult:
    return LoadResult(items=("id=1",), ok=True) if name == "a" else LoadResult()

# ❌ 错误 —— 三种形状；声明 -> dict 时最后一行本身就是类型错误
def load(name: str):
    if name == "a":
        return {"id": 1}
    if name == "b":
        return []
    return None
```

### F6 同一套规则真被两处用才抽函数，不抽薄包装

- 抽函数的判据是「规则真的一样」且复用 ≥ 2 处，不是「长得像」
- 只有一行、只被调一次的不抽，主流程不被只出现一次的名字切碎

```python
# ✅ 正确 —— 两处真的复用同一套规则
def validate_name(user: dict) -> None:
    if not user.get("name"):
        raise ValueError("名称不能为空")
    if len(user["name"]) > 50:
        raise ValueError("名称过长")

def process_admin(user: dict) -> str:
    validate_name(user)
    return "admin"

# ❌ 错误 —— 两处内联：给一个入口补了长度上限，另一个还是老规则
def process_admin(user: dict) -> str:
    if not user.get("name"):
        raise ValueError("名称不能为空")
    if len(user["name"]) > 50:
        raise ValueError("名称过长")
    return "admin"

def process_member(user: dict) -> str:
    if not user.get("name"):
        raise ValueError("名称不能为空")
    return "member"
```

### F7 按「会一起改的东西」分文件，不按目录对称性

- 短流水线留在一个业务文件里；只有被多处复用、变更节奏独立的工具才拆出去
- 拆分理由不是「目录好看」；反过来把数据库初始化、过滤、SDK 适配塞在一起也一样错

```text
# ✅ 正确
pipeline.py            # load / clean / export 三个 step + __main__ 编排，一起改
db_init.py             # 独立工具：被多个入口调用、规则固定
sdk_adapter.py         # 独立工具：隔离外部 SDK 的版本与认证细节

# ❌ 错误 —— 按阶段拆成薄文件，改一个字段名要开六个文件
pipeline/
  step1_load.py        # 12 行
  step2_clean.py       # 9 行
  step3_export.py      # 14 行
  main.py              # 20 行，只串三个 import
```

- 两个可观察信号：规则在别处也被用、变更节奏互不相干——占一个才拆

### H1 重构后逐项确认七件事没变

- 重构只改结构不改行为；动手前按七项逐一对照，不靠「看起来一样」
- 七项：返回值 / 副作用（次数与顺序）/ 求值顺序 / 惰性还是立即 / 异常类型与消息 / 日志·指标·重试 / 对外签名

```python
# ✅ 正确 —— 保持惰性，调用方行为不变
from typing import Iterator

def read_lines(fh) -> Iterator[str]:
    for ln in fh:
        yield ln.strip()

# ❌ 错误 —— 返回值一样，但「用到才算」变成「一次全算完」
def read_lines(fh) -> list[str]:
    return [ln.strip() for ln in fh]
```

- 处理 8GB 日志时，后者直接把内存打满；小样例上两者输出一字不差，测试也过
- 七项里只要有一项答不上来，这次改动先别合并

### H2 前置条件别一层层套，不满足就提前 return

- 一个前提一个 `if ...: return`，主流程留在最外层
- 每多一层缩进，读者脑内就多存一个「现在前提都成立」的假设

```python
# ✅ 正确
def process(order) -> str | None:
    if order is None:
        return None
    if not order.valid:
        return None
    if not order.items:
        return None
    return f"fulfilled:{len(order.items)}"

# ❌ 错误 —— 真正干活的在第 4 层，加一句审计日志要插进最里面
def process(order) -> str | None:
    if order is not None:
        if order.valid:
            if order.items:
                return f"fulfilled:{len(order.items)}"
    return None
```

### H3 一长串 `if 值 ==` 改成查表；形状分支用 `match-case`

- 值到值用字典：映射是数据，可枚举、可测试、加一项只改一行
- 分支条件是输入的形状（解构字典、序列、类实例）时用 `match-case`（3.10+）

```python
# ✅ 正确 —— 值到值
HANDLERS: dict[str, str] = {"start": "started", "stop": "stopped", "pause": "paused"}

def execute(action: str) -> str:
    return HANDLERS.get(action, "unknown")

# ✅ 正确 —— 形状分支，不是值相等
def describe(event: dict) -> str:
    match event:
        case {"type": "click", "x": int(x), "y": int(y)}:
            return f"click@{x},{y}"
        case {"type": str(kind)}:
            return f"other:{kind}"
        case _:
            return "unknown-shape"

# ❌ 错误 —— 加一种动作就要改函数体，顺序还藏着谁先命中
def execute(action: str) -> str:
    if action == "start":
        return "started"
    elif action == "stop":
        return "stopped"
    else:
        return "unknown"
```

- 分支里还有写日志、改状态、调接口这类动作时别硬塞进字典；把各分支抽成同签名的函数再放进表

### H4 能用 `sum` / `any` / `zip` / `enumerate` 就别手写循环

- 意图当函数名用：求和 `sum`、存在性 `any`、遍历带序号 `enumerate`、并行遍历 `zip`
- 空输入、短路、惰性这些边界行为由标准库保证，不用每处重新决定

```python
# ✅ 正确 —— 意图即函数名；短路与空表行为由标准库保证
total = sum(prices)
has_admin = any(u["role"] == "admin" for u in users)
top = max(prices, default=0)          # 空表返回 0，写在调用点上
for i, u in enumerate(users, start=1):
    ...

# ❌ 错误 —— 读的人要读完循环体才知道这是求和 / 存在性判断
total = 0
for p in prices:
    total += p

has_admin = False
for u in users:
    if u["role"] == "admin":
        has_admin = True
        break
```

- `sum` 从 `0` 起加，给字符串或列表求和会 `TypeError`；那种场景用 `"".join` 或 `list.extend`
- 流式处理（分组、切片、累积）用 `itertools` 的组合子，不会意外物化整表

### H5 别让数字和字符串裸奔在代码里，同一个语义值只定义一处

- 字面量给名字（模块常量全大写）；状态、类型这类值域固定的升级成 `IntEnum` / `StrEnum`
- 同一个语义值在十个文件里各写一遍，改值时必漏一处，且只在特定分支复现

```python
# ✅ 正确
from enum import IntEnum

class OrderStatus(IntEnum):
    PENDING = 1
    CONFIRMED = 2
    SHIPPED = 3

RATE_LIMIT_STATUS = 429
RATE_LIMIT_WAIT_SECONDS = 60

def label(status: int) -> str:
    return "已确认" if status == OrderStatus.CONFIRMED else "未知"

def backoff(code: int) -> int:
    return RATE_LIMIT_WAIT_SECONDS if code == RATE_LIMIT_STATUS else 0

# ❌ 错误 —— 60 的含义只活在写它那个人的脑子里
def backoff(code: int) -> int:
    return 60 if code == 429 else 0
```

- `0` / `1` / `""` 这种谁都懂的不用起名；严到什么程度是本规范的选择，可以放宽

### H6 四个「该拆了」的信号：嵌套 >3、分支 >4、函数 >30 行、参数 >5

- 超了就停下来解释一句为什么可以不拆，不是直接判错
- 四个数没有权威出处，是可调的经验值；值钱的是「能数出来」，不是具体数值

```python
# ❌ 超标的形状：嵌套 4 层、值分发 5 个分支
def process_all(data: dict) -> str:
    if data:                               # 1 层
        for key in data:                   # 2 层
            if key.startswith("x"):        # 3 层
                if data[key] is not None:  # 4 层 —— 超了（>3）
                    if key == "x1":
                        return "a"
                    elif key == "x2":
                        return "b"
                    elif key == "x3":
                        return "c"
                    elif key == "x4":
                        return "d"
                    elif key == "x5":      # 分支到第 5 个 —— 超了（>4）
                        return "e"
    return ""

# ✅ 拆完：每个函数只干一件事，数得清
def _pick(key: str) -> str:
    return {"x1": "a", "x2": "b", "x3": "c", "x4": "d", "x5": "e"}.get(key, "")

def process_all(data: dict) -> str:
    for key in data:
        if key.startswith("x") and data[key] is not None:
            return _pick(key)
    return ""
```

- 也别拿它当门槛：一个 35 行的直线流程，比一个 20 行的四层嵌套好读

### H7 只被用一次的中间变量可以删，但带着业务名字的那个别删

- 名字带来原表达式没有的信息才留：业务术语、复用点、调试锚点
- 只是把一句拆成两行、名字与表达式等价的，删掉

```python
# ✅ 正确 —— 该删：变量没带来新信息
def is_valid_age(age: int) -> bool:
    return 0 <= age <= 150        # 链式比较比 and 更贴合「区间」

# ✅ 正确 —— 该留：名字就是文档
def invoice_total(unit_price: float, quantity: int, tax_rate: float) -> float:
    subtotal = unit_price * quantity      # 税前小计：税率乘的是它
    return subtotal * (1 + tax_rate)

# ❌ 错误 —— 变量名与表达式等价，白加一层
def is_valid_age(age: int) -> bool:
    result = age >= 0 and age <= 150
    return result
```

- 删掉 `subtotal` 之后，后来者容易写成 `unit_price * (1 + tax_rate) * quantity`——数学等价，浮点结果不再逐位相同


### F8 路由函数只做校验与调用，业务在架构层

- 路由函数里只做三件事：接参数（请求体模型、依赖注入）、调业务、返回
- 进程级资源从 `app.state` 取（在 lifespan 里建），不在路由里连库、起客户端
- 返回：简单接口直接 `return` dict；字段多、要被前端或外部依赖、要裁掉内部字段时，在 `schema.py` 里定义响应模型

```python
# ✅ 正确 —— schema.py 里
from pydantic import BaseModel, Field

class AnswerRequest(BaseModel):                 # 请求体必须定义
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)

# ✅ 正确 —— router.py 里
@router.post("/answer")
async def answer(request: Request, body: AnswerRequest):
    pool = request.app.state.pool               # 只取，不在路由里连
    result = await answer_service(pool, body)   # 业务在架构层
    return {"answer": result.text, "sources": result.sources}

# ❌ 错误 —— 路由里连库、写业务、拼 SQL，接口一改就要动业务
@router.post("/answer")
async def answer(body: dict):
    conn = await asyncpg.connect(DATABASE_URL)  # 每请求连一次
    rows = await conn.fetch("select ... where q = $1", body["q"])
    return {"answer": rows[0]["text"]}
```

### F9 数据结构用 `dataclass` 还是 pydantic `BaseModel`

- **进出的边界**（HTTP 请求体、接口响应、配置、别人发的消息）用 `BaseModel`：它做校验与类型转换
- **自己造的内部数据**（层与层之间传的对象、函数返回值）用 `dataclass`：免样板、零第三方依赖、不跑校验
- 请求体必须是 `BaseModel`（见 [project.md](./project.md) FastAPI 节）；响应体按需

```python
# ✅ 正确 —— 边界：进来就验，"123" 被规范成 123
from pydantic import BaseModel, Field, ValidationError

class UserPayload(BaseModel):
    user_id: int
    name: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)

try:
    user = UserPayload(**json.loads(raw))
except ValidationError as exc:
    print(exc.errors())          # 逐字段列出问题与位置

# ✅ 正确 —— 内部：有名字、有类型、不拉依赖
from dataclasses import dataclass, field

@dataclass
class InternalJob:
    user_id: int
    tags: list[str] = field(default_factory=list)

# ❌ 错误 —— 拿 dataclass 收边界数据：它不做任何值校验
@dataclass
class UserPayload:
    user_id: int                 # 收到 "123" 也照收，到用的时候才炸
    name: str
```

- 反过来，在纯内部的地方到处上 `BaseModel`：多一个依赖、每次构造真跑一遍校验，而数据本来就是自己拼的
