# 异常

命中「写 `except`、谁兜底、换异常类型」时读本文。风格与怎么跑见 [SKILL.md](../SKILL.md)；单文件脚本的批处理见 [script.md](./script.md)。

### E1 不写裸 `except:`；只在主流程函数兜底，且必须打出 traceback

- 不写裸 `except:`；业务函数让异常冒泡，或转成调用方已约定的错误结构
- 只有主流程函数（按顺序调 step1、step2 的那个）统一兜底，且必须把 traceback 打出来

```python
# ✅ 正确
def parse_amount(text: str) -> int:
    return int(text)              # ValueError 交给调用方

def run(self) -> dict:
    try:
        self.step1_load()
    except Exception:
        print(traceback.format_exc())     # 位置与调用栈完整留痕
        self.result["message"] = "流程异常终止"
    return self.result

# ❌ 错误
for row in rows:
    try:
        process(row)
    except:                       # 也抓 KeyboardInterrupt / SystemExit
        pass                      # 失败被吞，最后只看到总数为 0
```

### E2 换异常类型时写 `raise ... from e`

- 把底层异常换成自己的异常时写 `raise 新异常 from e`
- 有意不展示原因时写 `from None`，并把相关信息搬进新异常

```python
# ✅ 正确
try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    raise ValidationError("JSON 格式无效") from e

# ✅ 正确 —— 有意不展示原因，写出来，别让它看起来像忘了
except KeyError:
    raise NotFoundError(f"缓存里没有 {key}") from None

# ❌ 错误
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    raise ValidationError("body 格式无效")
```
