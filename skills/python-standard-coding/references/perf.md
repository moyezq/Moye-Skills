# 性能

命中「大文件、大结果集、比内存大的数组」时读本文。风格与怎么跑见 [SKILL.md](../SKILL.md)；容器选择见 [containers.md](./containers.md)。

### P1 大文件、大结果集用生成器流式处理

- 逐条处理、流式聚合就用生成器：内存占用与数据规模脱钩
- 需要随机取（`rows[0]`）或多遍遍历时显式物化，并把这件事写进签名

```python
# ✅ 正确 —— 一次只持有一行
from collections.abc import Iterator

def read_stream(p: str) -> Iterator[str]:
    with open(p, encoding="utf-8") as fh:
        for ln in fh:
            yield ln.strip()

total = sum(len(ln) for ln in read_stream("big.txt"))    # 生成器表达式同样不物化

# ❌ 错误 —— 内存占用与文件大小成正比
def read_all(p: str) -> list[str]:
    with open(p, encoding="utf-8") as fh:
        return [ln.strip() for ln in fh]
```

- 生成器只能消费一次：签名写着 `-> list[str]` 而调用方遍历两遍时，改成生成器比不改更危险
- 确实要多遍就显式写 `rows = list(read_stream("big.txt"))`

### P4 比内存大的数组用 `numpy.memmap` 或分块读，不整表进内存

- 要随机取（`mm[:1000]`）用 `np.memmap` 内存映射；只从头到尾扫一遍用分块读
- 内存占用从「等于数组大小」变成「等于一个块」；文本、压缩流这类不支持映射的格式只能分块

```python
# ✅ 正确 —— 内存映射 + 分块累加，常驻内存只是一个块
import numpy as np

def mean_memmap(p: str) -> float:
    mm = np.memmap(p, dtype=np.float32, mode="r")
    total = 0.0
    step = 1_000_000
    for start in range(0, mm.shape[0], step):
        total += float(mm[start:start + step].sum())
    return total / mm.shape[0]

# ❌ 错误 —— 峰值内存 ≈ 数组大小；40G 文件在 32G 机器上第一步就崩
def mean_all(p: str) -> float:
    arr = np.load(p)
    return float(arr.mean())
```

- 本地拿 1% 采样数据跑永远正常；上线换全量时崩在加载这一步，而报错看起来像后面的问题
