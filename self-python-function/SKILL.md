---
name: self-python-function
description: Python 函数、方法与类怎么写。改 def、class、工具函数、FastAPI 路由处理时查阅；用户嫌模块或函数拆太碎时也查阅（即使用户没说代码规范）。风格与怎么跑见 self-python-style；脚本怎么分阶段见 self-python-script；目录与小服务见 self-python-project。
---

# Python 函数、方法与类

管 **一个函数、方法、类怎么写**。风格与怎么跑见 `self-python-style`；脚本切步见 `self-python-script`；仓库目录与何时用流水线类见 `self-python-project`；12 条判断见 `self-code-principles`。

完成标准：改到的每个 def / class / 路由都过一遍下面的怎么做。文件级拆分不在本文件。

## 何时用

**用**：编写或修改 Python 函数、方法、类、FastAPI 路由处理；或嫌拆太碎。

风格（docstring、注释、顺序、命名、信任上游字段、运行参数、print 与 logger）见 `self-python-style`，不替代本文件。脚本切步、目录形态分别再加读对应 skill。

---

## 什么时候才抽函数 / 方法

抽函数是为了 **至少两处真正复用同一套规则**，不是为每个动作起一个名字。

不要抽薄包装：只被一处调用一次；为「以后可能复用」先准备的私有函数；把一段连续逻辑拆成多个只被串联调用的 `fetch_x` / `handle_x`。

可以留：两处以上调用、且规则固定的协议细节（签名头、设备指纹格式、统一非 200 报错）。

**字段与返回值**：以调用方、fixtures、scheme 已固定的名字为准；不要在重构时顺手换一套近义字段名却只改到一半。

同一条短流水线不要拆成多个只被编排层调用一次的文件；文件级拆分见 `self-python-project`。脚本场景下「一步一个 step、线程池用嵌套 def」见 `self-python-script`。

## 流水线类（有类的时候怎么写）

**何时用这种类** 由 `self-python-project` 决定。这里只定类内部习惯：

```python
class ReportPipeline:
    def step1_load(self) -> bool: ...
    def step2_process(self) -> bool: ...

    async def run(self) -> dict:
        try:
            if not self.step1_load():
                return self.result
            if not await self.step2_process():
                return self.result
            return self.result
        except Exception:
            print(traceback.format_exc())
            self.result["message"] = "流程异常终止"
            return self.result
```

- 每步返回 `bool`；终止时写 `self.result["message"]` 并 `return False`。
- `run()` 只编排与统一异常处理，不写业务细节。
- 共享状态放实例属性，不要靠一长串参数在步骤间来回传同一份结果袋。

单文件脚本不要为了「看起来像类」而套这层；那种入口见 `self-python-script`。

## 编码

同目录已有等价函数就调用，不平行再写一份。`print` 还是 logger 见 `self-python-style`。

## 异常与资源

- 捕获写得出名字的异常类型；需要保留原因时用 `raise ... from e`。
- 只有编排层（如流水线 `run()`）才统一兜底，且必须把 traceback 打出来（见「流水线类」示例）。业务函数让异常冒泡，或转成调用方已约定的错误结构。
- 打开文件、套接字、临时目录用 `with`；FastAPI 里进程级连接放项目已有的 lifespan。

## FastAPI：路由与 schema

**适用**：编写或修改路由处理函数、Pydantic schema、依赖函数。生产约定（Apollo、业务码、网关、队列）以当前项目为准，目录形态见 `self-python-project`。

**请求体**

- 入口用 Pydantic `BaseModel` 声明契约：有哪些字段、哪些必填。
- 字段稳定、含义固定的（URL、枚举 mode、必填 id）可用 `Field` / `Literal`。
- 内部 RPC 里形状随业务变化的载荷（如 `JobRequest.data: Any`、SQL 字符串）不要堆 `EmailStr`、用户名正则、年龄区间。形状校验和业务校验分开。

**异步与阻塞**

- 多路彼此独立的 I/O 用 `asyncio.gather`；需要限时用 `asyncio.wait_for`。
- 必须调用同步 SDK 时，用 `asyncio.to_thread`（或项目里已有的线程池），不要新造一套 `run_in_threadpool` 包装。
- `async def` 里的等待用 `await asyncio.sleep` / 异步客户端；阻塞 I/O（`time.sleep`、同步 `requests`、同步 OSS/SDK、同步 ffmpeg）走上一行的线程池或项目已有队列。
- 转码、模型推理等 CPU/重活走项目已有队列或独立 worker；HTTP 只入队、查状态。
- 依赖是否写成 `async` 看它是否真有 `await`。同步 SQLAlchemy `Session` 的 `Depends(get_db)` 保持同步。

**能跑的保持**

- 不为内部一次性 POST 抽链式 `valid_xxx_id`；没有跨路由复用的资源 ID 就不上这套 Depends。
- 已有返回值（模型实例或 dict、业务码或 HTTP 状态）能跑就保持；新接口可直接 `return dict`。
- 不必给每个内部接口写满 `responses={}`。
