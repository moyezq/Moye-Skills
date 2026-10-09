# 容器与数据结构

命中「选容器、判成员、计数、分组、队列、边界数据校验、路径」时读本文。风格与怎么跑见 [SKILL.md](../SKILL.md)；类型标注见 [typing.md](./typing.md)。

### D1 只判「在不在」用 `set`，不用 `list`

- 成员判断的常量写成 `set` / `frozenset`：哈希查找，与元素个数无关
- 还要按下标取、要排序、要保持顺序时仍然用 `list`

```python
# ✅ 正确
VALID_SET = {"pending", "active", "closed", "archived", "deleted"}

def ok(status: str) -> bool:
    return status in VALID_SET

# ❌ 错误 —— 每次判成员都线性扫描
VALID_LIST = ["pending", "active", "closed", "archived", "deleted"]

def ok(status: str) -> bool:
    return status in VALID_LIST
```

- 合法值从 5 个涨到 50 个（白名单、配置项）时代价线性放大，而代码看着没变
- 集合顺带去重：重复写两遍同一个值不会有人发现；`frozenset` 还能防误改

### D2 计数用 `Counter`，不手写 `counts[w] = counts.get(w, 0) + 1`

- 计数用 `Counter`：意图就是类型名，还自带排行榜与两表相加
- 缺失键返回 `0` 而不是 `KeyError`

```python
# ✅ 正确
from collections import Counter

c = Counter(words)
c["missing"]            # 0，不抛 KeyError
c.most_common(2)        # [('blue', 3), ('red', 2)]
(c + Counter(["red"])).most_common(1)     # 两张频次表直接相加

# ❌ 错误 —— 漏了 .get(w, 0) 就只在「该键首次出现」时炸
counts: dict[str, int] = {}
for w in words:
    counts[w] = counts[w] + 1
```

- 同一文件三处各写一遍计数时，忘写 `.get(w, 0)` 的那处只在生产数据上炸

### D3 分组用 `defaultdict(list)`，桶的工厂写在声明处

- 分组用 `defaultdict(list)`：新桶怎么建只在声明处说一次，循环体只剩业务
- 要把这张表返回给别的函数时先 `dict(by_key)`，否则调用方读一个不存在的键会静默多出一个空桶

```python
# ✅ 正确
from collections import defaultdict

by_key: defaultdict[str, list[int]] = defaultdict(list)
for key, value in rows:
    by_key[key].append(value)

# ❌ 错误 —— 桶的初始化散在循环里，复制到第二个函数时最容易漏
groups: dict[str, list[int]] = {}
for key, value in rows:
    if key not in groups:
        groups[key] = []
    groups[key].append(value)
```

- 漏掉初始化的那份代码只在「某个分组首次出现」时 `KeyError`，取决于输入数据顺序

### D4 队列两头进出用 `deque`，不用 `list.pop(0)`

- 只从两端进出用 `deque`：`append` / `pop` / `appendleft` / `popleft` 都是 O(1)
- 要按 `q[500]` 随机取中间元素时仍用 `list`（`deque` 中部索引是 O(n)）

```python
# ✅ 正确
from collections import deque

q = deque(items)
while q:
    total += q.popleft()

window = deque(maxlen=100)     # 只留最近 100 条的滑动窗口，一行

# ❌ 错误 —— 每次 pop(0) 都要把剩下的元素整体前移一格，整体 O(n²)
q = list(items)
while q:
    total += q.pop(0)
```

- 一千条是毫秒级、完全看不出来；上线后队列涨到十万条整段卡住且没有异常

### D6 路径用 `pathlib`，不拼字符串

- 拼接、拆解、读写、遍历都用 `Path`：`/` 负责拼接并规范化，`.name` / `.suffix` / `.parent` 负责拆解
- 与只收 `str` 的老接口交界时，在边界显式转一次 `str(p)` 或 `os.fspath(p)`

```python
# ✅ 正确
from pathlib import Path

p = Path("data") / "result" / name
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text("{}", encoding="utf-8")
print(p.name, p.suffix, sorted(x.name for x in Path("data").rglob("*.json")))

# ❌ 错误 —— Windows 上得到 C:\data/output.txt 这种混合分隔符
p = "data" + "/" + name
seen[p] = True          # 与 C:\data\output.txt 不是同一个字符串
```

- 同一个文件被两种写法表示时，在「已处理集合」里成了两个条目，于是被处理两遍
