# 类型标注

命中「写或改类型标注、改返回值形状、`Protocol` / `TypedDict` / `Final`」时读本文。风格与怎么跑见 [SKILL.md](../SKILL.md)；异常类型见 [exceptions.md](./exceptions.md)。

### T2 每个参数和返回值都标类型，`-> None` 也写

- 所有参数、返回值都写；没有返回值就写 `-> None`
- `__init__` 必须标，否则其实例属性被推断成 `Any`，之后 `x.value + 1` 一律不报错

```python
# ✅ 正确
def total(rows: list[dict[str, int]]) -> int:
    return sum(r["amount"] for r in rows)

def log_once(message: str) -> None:
    print(message)

class Order:
    def __init__(self, order_id: str) -> None:
        self.order_id = order_id

# ❌ 错误 —— 这个 __init__ 整个不被检查
class Order:
    def __init__(self, order_id):
        self.order_id = order_id

order = Order(1)
order.order_id + 1        # 检查器不报错，运行时 TypeError
```

### T3 只读参数标能力：只遍历用 `Iterable`，要下标用 `Sequence`

- 参数标注描述「函数需要什么能力」，不是「调用方给了什么容器」
- 只读参数不标具体容器类型：`Iterable[X]` 只承诺能遍历，`Sequence[X]` 再承诺有长度和下标

```python
# ✅ 正确
from collections.abc import Iterable, Sequence

def total(rows: Iterable[dict]) -> int:
    return sum(r["amount"] for r in rows)

def first_amount(rows: Sequence[dict]) -> int:
    return rows[0]["amount"]

# ❌ 错误 —— 只读却写 list，list 是能改的所以不变，list[OrderRow] 被拒
def first_amount(rows: list[dict]) -> int:
    return rows[0]["amount"]
```

- 把只读参数写成 `list[X]`，`tuple` 与元素更具体的列表都会被拒，调用方被迫复制一份

### T4 改了入参容器就得如实标：`MutableSequence` / `MutableMapping`

- 函数体内会改容器（`append` / `update` / `pop`）就标可变类型，把「我改了你给的东西」写在签名上
- 优先不改入参、返回一个新容器，此时参数仍可标只读类型

```python
# ✅ 正确 —— 真要改就写可变抽象类型
from collections.abc import MutableSequence

def add_tag(tags: MutableSequence[str], tag: str) -> None:
    tags.append(tag)

# ✅ 正确 —— 大多数时候更好：不动别人给的对象
from collections.abc import Sequence

def with_tag(tags: Sequence[str], tag: str) -> list[str]:
    return [*tags, tag]

# ❌ 错误 —— 标了只读却在改；加 # type: ignore 只是把副作用藏起来
from collections.abc import Sequence

def add_tag(tags: Sequence[str], tag: str) -> None:
    tags.append(tag)      # 检查器报 Sequence 没有 append
```

### T5 容器默认参数写 `None`，在函数里建

- 默认值不写 `[]` / `{}` / `set()`，写 `None`，进函数体再建
- 所有调用共享同一个默认对象，第二次调用会带上第一次留下的数据

```python
# ✅ 正确
def add_item(item: str, container: list[str] | None = None) -> list[str]:
    if container is None:
        container = []
    container.append(item)
    return container

# ❌ 错误
def add_item(item: str, container: list[str] = []) -> list[str]:
    container.append(item)
    return container

add_item("a")     # ['a']
add_item("b")     # ['a', 'b'] —— 上一次的元素还在
```

- 字典、集合、自定义可变对象当默认值同理；单次运行永远正常，连着跑才复现

### T6 类型变量叫 `T` / `KT` / `VT`，协变加 `_co`

- 单一任意类型用 `T`；映射的键、值用 `KT`、`VT`
- 协变加 `_co`，逆变加 `_contra`

```python
# ✅ 正确
from typing import TypeVar

T = TypeVar("T")
KT = TypeVar("KT")
VT = TypeVar("VT")
VT_co = TypeVar("VT_co", covariant=True)
KT_contra = TypeVar("KT_contra", contravariant=True)

def first(items: list[T]) -> T:          # 传进来什么元素，就返回什么元素
    return items[0]

# ❌ 错误 —— 名字不表达「这几个位置是同一个类型」，方差也看不出
X = TypeVar("X")
A = TypeVar("A", covariant=True)
```

### T7 `# type: ignore` 必须带规则码

- 不写裸 `# type: ignore`，写成 `# type: ignore[规则码]`
- 规则码本身记录了这条豁免是为了绕开哪一类问题

```python
# ✅ 正确
import some_lib                                  # type: ignore[import-not-found]

class Child(Base):
    def handle(self, x: list[int]) -> None: ...  # type: ignore[override]

# 整个文件范围时也用带码形式
# mypy: disable-error-code="truthy-bool"

# ❌ 错误 —— 整行关闭，将来引入的真错误一起被静音
import some_lib                                  # type: ignore
```

### T8 接口形状用 `Protocol`，不要求对方继承你的基类

- 声明「需要哪些成员」用 `Protocol`，具备这些成员的类型自动合格
- 第三方类不能改继承关系，用 `Protocol` 才装得进来；要求对方继承你的类会逼出适配器或 `Any`

```python
# ✅ 正确
from typing import Protocol

class Serializable(Protocol):
    def to_dict(self) -> dict: ...

def save(obj: Serializable) -> None:
    print(obj.to_dict())

# ❌ 错误 —— 要求显式继承；第三方类的祖谱你改不了，只能包一层或标 Any
from abc import ABC, abstractmethod

class Serializable(ABC):
    @abstractmethod
    def to_dict(self) -> dict: ...
```

- Protocol 类不能实例化；要 `isinstance` 检查得加 `@runtime_checkable`
- 需要默认实现或在运行期按类型注册时，仍然用抽象基类

### T9 固定键的字典用 `TypedDict`；`Any` 只留真正动态处

- 键集合固定的数据（JSON 载荷、接口参数）用 `TypedDict` 写清每个键的类型，不用 `dict[str, Any]`
- `Any` 只留给形状确实不定的位置，并在那一行写明原因
- 可选键用 `NotRequired`；`Any` 上做的任何操作检查器都不管，而且会顺着调用链传染

```python
# ✅ 正确
from typing import NotRequired, TypedDict

class UserUpdates(TypedDict):
    name: str
    email: NotRequired[str]

def update_user(user_id: int, updates: UserUpdates) -> None: ...

# ✅ 正确 —— Any 只出现在真正动态的位置，并写明为什么
def call_legacy(payload: Any) -> None:   # 上游协议未定型，形状随版本变
    ...

# ❌ 错误 —— 键名和值类型全不检查
def update_user(user_id: int, updates: dict[str, Any]) -> None: ...

update_user(1, {"nmae": "张三"})     # 拼错不报错，字段静默丢掉
```

- 版本：class 语法 3.8 起；`NotRequired` / `Required` 3.11 起；`ReadOnly` 3.13 起
- 运行期它就是普通 `dict`，与 JSON 兼容，没有额外开销

### T10 模块常量与类属性都标类型，不会重新赋值的写 `Final`

- 模块常量、类属性都标类型；空容器尤其要标，否则被推断成 `Any`
- 不会重新赋值的写 `Final`，常量被谁改了由检查器兜住

```python
# ✅ 正确
from typing import Final

MAX_RETRIES: Final[int] = 3
DEFAULT_TIMEOUT: Final[float] = 30.0
SUPPORTED: Final[frozenset[str]] = frozenset({"json", "csv"})

class Config:
    DEFAULT_PORT: Final[int] = 8080

pending: list[str] = []          # 空容器不标就是 Any

# ❌ 错误
MAX_RETRIES = "3"                # 想写的是 3，没人报错
MAX_RETRIES = 5                  # 重新赋值也没人报错
```

- `Final` 只保证名字不被重新赋值，不保证值不可变：`x: Final[list[int]] = []` 之后 `x.append(1)` 仍然合法，要连内容一起管住得写 `Final[Sequence[int]]`

