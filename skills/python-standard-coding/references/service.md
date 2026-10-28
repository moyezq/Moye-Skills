# 调研用的最小服务

一个只听 `127.0.0.1` 的 HTTP 服务，用来把「一次请求」那类脚本接到一个还没有 HTTP 入口的东西上：模型权重、一个库、一条外站协议。**它不进产品链路**，落盘形态与生产服务不同。

完成标准：开写前契约表已填；主流程是同步函数且配了锁；模型句柄在 `lifespan` 里加载、路由从 `app.state` 取；下游会抛的 `ValueError` 已转 422；探针跑得通、退出码 0；换实现前后同一个探针输出逐位相同。

## 何时用

**用**：要弄清一个模型、一套权重、一条外站协议究竟怎么工作，而对方只给函数或权重，需要起一个接口拿脚本去打。用户说「起个测试服务」「写个 mock 服务」「把这个模型包一层接口」「先用最小的方式验证一下」。

**不用**：会进产品链路的服务——层与模块、接口写法、启动文件见 [prd-fastapi.md](./prd-fastapi.md)。目标已经有了现成端点，只是要打一次看一眼：见 [script.md](./script.md)「一次请求」。

## 判据：它会不会进产品链路

会——按 [prd-fastapi.md](./prd-fastapi.md) 分层、写接口；通用规则（配置文件、`.env`）见 [project.md](./project.md)。启动文件放仓根，容器、密钥、部署都要考虑。

不会——读本文。落盘是 `scripts/<名字>/` 一个目录：

```
scripts/<名字>/
├── serve_xxx.py      服务：路由、校验、响应体
├── probe_xxx.py      探针：固定用例、打印原文、退出码
├── pyproject.toml    本目录自己的依赖
├── .venv/            本目录自己的解释器
└── models/           权重、缓存，不进仓
```

启动走 `uv run python serve_xxx.py`，不经仓根，也不 import 仓里其它包。环境、权重、服务、探针都在这一层，缺哪样就当场报错，不往别处找退路。

## 先钉契约，再写服务

动手前填完这张表；填不出说明还没到写服务的时候。

| 路由 | 方法 | 请求字段 | 成功响应 | 错误码 |
|---|---|---|---|---|
| `/v1/xxx` | POST | `state`、`questions` | `answers`、`usage` | 422 |

✅ 先写探针：它发什么、解析什么，由这张表决定。
❌ 先写服务，再按实现反推探针该发什么。

换实现（换框架、换后端、换模型）时，同一个探针跑两遍：输入相同、输出逐位相同，才算换完。

## 阻塞计算写成同步路由

推理、CPU 密集、同步 IO 用 `def`，外面配一把锁串行。

```python
# ✅
LOCK = threading.Lock()

@app.post("/v1/xxx")
def xxx(body: XxxRequest, request: Request) -> dict:
    with LOCK:
        return compute(model, body.state, body.questions)
```

```python
# ❌ 阻塞调用放进 async def：事件循环被占住，探活端点一起卡
@app.post("/v1/xxx")
async def xxx(body: XxxRequest) -> dict:
    return compute(model, body.state, body.questions)
```

同步路由由框架丢进线程池，锁保证同一时刻只有一个前向在算，并发请求排队而不是一起抢显存。

## 进程级资源放 lifespan

```python
# ✅
@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    application.state.model = load_model(...)
    yield

app = FastAPI(lifespan=lifespan)
```

```python
# ❌ 模块级加载：import 一次就吃掉整个模型，接口形状没法单独看
_MODEL = load_model(...)
```

放进 `lifespan` 之后，`import serve_xxx` 不读权重，`app.openapi()`、测试客户端、`/docs` 都能在没有模型的机器上跑。

## 会变 500 的输入拦成 422

请求体用模型校验；下游抛 `ValueError` 的在路由里转 422；缺了就算不出答案的子字段，在校验器里拦。

```python
# ✅
try:
    answers, input_tokens, elapsed = compute(model, body.state, questions)
except ValueError as error:
    raise HTTPException(status_code=422, detail=str(error)) from error
```

```python
# ❌ 让它冒到框架：500 + traceback，调用方分不清是自己发错还是服务坏了
answers, input_tokens, elapsed = compute(model, body.state, questions)
```

## 探针是验收

探针固定几条用例，打印请求原文与响应原文，退出码 0 = 全过、1 = 有失败。

✅ `uv run python probe_xxx.py` 退出码 0，关键数值与换实现前逐位相同。
❌ 看到 HTTP 200 就报「跑通了」。

探针里那几条用例就是你手上唯一的回归基线，换完实现要能一眼比出数值差。

## 不加没有调用方的东西

CORS、鉴权、请求 id、限流、健康检查、状态页：先说出谁在用、在哪一行，说不出就不加。

## 运行上限

服务进程不套 [script.md](./script.md)「运行上限」里的 5 分钟自杀——它要一直听。上限改成每个请求一个：服务侧给单次前向设一个，探针侧 `timeout=` 设一个。

## 路由按步骤注释

主流程按步号排开，一行一条注释；单行包装不抽成函数，密集表达式拆中间变量。

✅ 五步五行注释，读者一眼数得出几步。
❌ 每步包一个函数，主流程变成一串跳转。

写完回头对一遍「先钉契约」那张表的字段名与错误码。
