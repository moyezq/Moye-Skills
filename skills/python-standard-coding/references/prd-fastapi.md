# 生产标准的 FastAPI 服务

会进产品链路的后端服务：层与模块怎么切、目录长什么样、接口怎么写、前后端同仓怎么放。调研、验证用的最小服务不走本文，见 [service.md](./service.md)。

配置文件、`.env`、`scripts/`、启动文件命名、依赖这些通用规则在 [project.md](./project.md)，对本文仍然生效。文档（README、ADR、`architecture.md`、`pipelines.md`、`todo.md`、最小视图）归项目文档规范。

完成标准：层与模块按数据流切、目录结构确定；接口落在模块的 `router.py` + `schema.py`；请求体是模型；启动文件只做四件事并写明 host 与 port；进程级资源在 `lifespan` 里建、路由从 `app.state` 取。

## 何时用

**用**：新建或整理一个要上线的后端服务——纯后端，或前后端同仓。加模块、拆模块、改目录、加接口、写启动文件时。

**不用**：调研用的最小服务，见 [service.md](./service.md)。单文件脚本，见 [script.md](./script.md)。只改函数内部或数据模型，见 [function.md](./function.md)。

## 层和模块怎么切：照 OSI 七层模型那种分法

目录名不是重点，**分层分模块的方式**才是。可以直接借用 OSI 七层模型那套思路：

- **分层** = 按数据流经过的处理阶段从上往下叠，每层只跟相邻层说话。请求进来，逐层往下处理，逐层往上返回。层与层之间是**接口**关系，不是「谁调用谁的工具函数」。
- **模块** = 同一层里按职责切开的小块，每块只干一件事、有自己的入口。一块内部的实现细节不外泄给同层的其它块。
- 判断自己切得对不对，问两句：**这一层换个实现（换向量库、换模型），上面几层要不要跟着改？** 要改说明层没切干净。**这一块被同层另一块直接 import 了内部函数吗？** 有说明模块边界破了。

用这套分法，一个 RAG 系统自然会得到「离线（入库）」与「在线（问答）」两条链，每条链下面才是阶段、阶段下面是模块。具体叫什么名字随项目，**结构关系不变**。

下面这棵树来自一套真实迭代出来的 RAG 项目（前后端同仓），只作**参考**：它带着那个项目的技术选型（`lancedb`、`bge-m3`、Vite）与当时的取舍，**别的项目不必照搬目录名，甚至别的 RAG 项目也不一定这么分**——要拿走的是它的分层分模块方式。

```plaintext
README.md                  # 人读写法见邻域入口 README-FORMAT
CONTEXT.md  DESIGN.md
AGENTS.md                  # 给 AI 的项目规矩
conf/
  base.py                  # ROOT 等要推算的值
  config.yaml              # 各环境相同的公共常量
.env  .env_example
docs/                      # 架构、ADR、术语、待办方向（写法规矩归项目文档规范）
  architecture.md
  todo.md                  # 本阶段打算做的方向
data/                      # 脚本与服务的输入产出（见 script.md）
  source/  result/  lancedb/
offline/                   # 架构层：离线入库链
  extract/                 # 模块：文件下载、基础信息、按类型读取、关键信息抽取
  vector/                  # 模块：分块、向量化、入库
  store/                   # 模块：键值存储
online/                    # 架构层：在线问答链
  intent/                  # 模块：分类、改写
  recall/                  # 模块：向量 + 关键词召回
  rerank/                  # 模块：精排、同节邻块
  filter/                  # 模块：标签过滤
  prompt/                  # 模块：提示组装
  generate/                # 模块：调用模型出答案
embed/                     # 架构层：嵌入服务（独立进程，被离线与在线共用）
web/                       # 前端（前后端同仓时才有）
  src/  package.json  vite.config.ts
scripts/                   # 跑完就退出的入口（见 project.md 通用规则 3）
  backup/url_to_knowledge.py
tests/
ask_server.py              # 服务启动文件（多服务时按 服务名_server.py 命名）
embed_server.py
start_all.py               # 前后端一起起，只为少几步调试（见「前后端同仓」第 3 条）
requirements.txt
main.py                    # 单服务项目才用这个命名
```

- 这棵树里 `offline/` `online/` 是**按数据流的阶段**分的架构层，不是按技术类型分的。别建 `models/` `services/` `handlers/` 这种横切目录当架构层。
- `embed/` 单独成层，是因为它被两条链共用、且是独立进程；被多层共用的东西才值得提出来当一层。
- 前端目录名随项目（`web/`、`frontend/` 都行），**关键是后端与前端在仓库里各自有一块完整地盘**，见「前后端同仓」。
- 没有前端时，架构层直接放在仓库根目录下，不建 `backend/` 和 `frontend/`。

## 接口写在哪：`router.py` 与 `schema.py`

每个对外提供接口的模块目录里各放一份。

```plaintext
online/generate/
  __init__.py
  answer.py                # 本模块的业务实现
  router.py                # 对外接口：路径、方法、状态码
  schema.py                # 请求体定义（响应体按需）
```

- 不在仓库根再铺一套 `routers/<模块>/`——那样「这个接口属于哪一层」要跨目录对。
- 一个模块只有一个 `router.py`；接口多了先用注释分段，别按接口再拆文件。

`schema.py` 里请求体定义成模型。响应体允许直接 `return`——简单接口为了返一个 dict 就再定义响应模型，调试时反而多一层要对照的东西。返回字段多、要被前端或外部依赖、要裁掉内部字段时，才值得定义响应模型。

路由函数本身怎么写、`BaseModel` 与 `dataclass` 怎么分工，见 [function.md](./function.md)。

## 启动文件只做四件事

`main.py` 或 `服务名_server.py` 只做四件事：创建应用、挂中间件、`include_router`、注册生命周期，并写明本服务的 host 和 port。业务实现放架构层或模块层。

host 和 port 不写进 `config.yaml`（见 [project.md](./project.md) 通用规则 1），生产放 Dockerfile。

## 进程级资源放 `lifespan`

连接池、向量库客户端、模型句柄在 `lifespan` 里建一次，路由只从应用状态取。每请求一份的资源（事务、临时文件）在依赖或路由内用 `with` 管住。

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_pool()          # 进程级：建一次
    try:
        yield
    finally:
        await app.state.pool.close()              # 退出时收干净

app = FastAPI(lifespan=lifespan)
app.include_router(generate.router, prefix="/generate", tags=["generate"])

@app.post("/generate/answer")
async def answer(request: Request, body: AnswerRequest):     # 请求体来自 schema.py
    pool = request.app.state.pool                            # 只取，不在路由里连
    result = await answer_service(pool, body)                # 业务在架构层
    return {"answer": result.text, "sources": result.sources}  # 简单响应直接返回

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 前后端同仓

前后端分离且归在同一仓库时读本节。通用规则仍生效。

1. **前端、后端必须分离，只通过协议通信。** 后端绝不能 `import` 前端的东西，前端也绝不能 `import` 后端的 Python 代码；两边说话只走 HTTP、WebSocket、MCP 这类协议。这不是「推荐」——前端是另一套运行时，跨语言 import 根本不存在。

2. 目录分法：前端一块地、后端一块地，每块内部再分层分模块。

```plaintext
web/                       # 前端一块地（目录名随项目：web/ 或 frontend/）
  src/
  package.json
  vite.config.ts
backend/                   # 后端一块地（前后端同仓时才需要这一级）
  rag/                     # 多服务时才有这一级「服务名」
    embedding/             # 架构层
      extract/             # 模块层
    retrieval/
  main.py                  # 后端自己的启动文件也放这里
start_all.py               # 仓库根：前后端一起起（见第 3 条）
```

- 单服务不需要「服务名」这一级。
- 后端内部的层与模块怎么切，同上面「层和模块怎么切」。
- `utils/` 是**后端**的工具文件夹命名习惯，与前端无关；前端自己的工具按前端生态的写法放（例如 `src/lib/`）。

3. **后端启动文件在 `backend/` 里放一份；仓库根目录放的是「前后端一起启动」的文件**，目的是减少调试这个项目所需的步骤——一条命令把两边都拉起来。仓库根不放后端服务的实现入口，`backend/main.py`（或 `backend/服务名_server.py`）才是。

4. 接口形状以 `backend` 的 `schema.py` 为准；前端那边自己写一遍类型（或用 OpenAPI 生成），不要跨语言共享文件。真要共享的只有常量与文案这类纯数据，放一处、两边各自读。

5. 只被一个模块使用的工具放该模块目录；被同一服务多个架构层共用的，在该服务文件夹下建 `utils/`。
