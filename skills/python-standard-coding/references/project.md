# Python 项目结构与设计规范

命中「新建/整理目录、加模块、写改 README、FastAPI、前后端同仓」时读本文。项目文档（术语、ADR、目标架构）按产物写进 `CONTEXT.md` / `docs/`；单文件脚本见 [script.md](./script.md)；函数与数据模型怎么写见 [function.md](./function.md)。

完成标准：新建或改目录时通用规则每条都套上；写改 README 已按邻域入口的 README-FORMAT 过一遍；命中 FastAPI 或前后端同仓时已读对应节。

## 何时用

**用**：新建项目、加模块、设计目录、整理已有仓、改目录。写或改 README 时：目录与依赖仍听本文，人读正文结构听项目文档 skill 的 README-FORMAT（邻域入口：`project-docs` → `README-FORMAT.md`）。

**不用**：单文件分阶段脚本（见 [script.md](./script.md)）。只改函数内部、不改目录。只改通用风格 / 怎么跑，不动目录与 README 时。

---

## 通用规则

1. 项目的配置统一放在根目录的 `conf` 文件夹中，并按下面分类，不要混放。
   - 随运行环境变化、要从本机推算的值，放在 `conf/base.py`。例如项目根目录 ROOT：用 `Path(__file__).resolve()` 推算，不要把盘符写进 yaml。把仓库根加入 `sys.path` 也写在这里。启动文件和脚本引用这里的 ROOT，不要每个文件再写一遍。
   - 本服务的 host、port 直接写在对应的 `main.py` 或 `服务名_server.py` 里。本地不常改；生产放 Dockerfile。不要写进 `config.yaml`。
   - `conf/config.yaml` 只放各环境相同、属于本项目自己的公共常量，例如相对数据目录、模型目录名。不要放 ROOT、host、port、第三方地址、密钥。
2. 第三方对接配置和隐私配置统一放在根目录 `.env`；模板放根目录 `.env_example`。
   - 第三方对接：外仓 HTTP 地址这类对接参数。
   - 隐私配置：API Key、Token、填了密钥的别人家 `.env` 路径。不要写进 `config.yaml`，也不要在 yaml 里指向另一份带密钥的 `.env`。
3. 项目的层/模块测试文件，统一放在根目录 `scripts` 中。跑完就退出的入库、评测、探测也放这里。这些入口脚本的文件头怎么写见 [script.md](./script.md)。
4. 如果是单服务的项目，根目录启动文件统一使用 `main.py` 命名；如果是多服务项目，根目录放多个服务的启动文件，以 `服务名_server.py` 命名。启动文件只负责启动服务、写明 host 和 port、挂路由和生命周期。业务实现放在架构层或模块层目录里。不要用 `python 子目录/xxx.py` 启动服务。同一个进程不要在包内再留一份 `__main__`。
5. 项目的设计文档统一放在 `docs` 中：`docs/architecture.md`、`docs/adr.md`、`docs/history.md`、`docs/pipelines.md`。待办方向按需写 `docs/todo.md`，不要放仓根。架构图走最小视图，不写进 `architecture.md`。
6. 没有前端时，不建 `frontend/` 和 `backend/`。架构层直接放在仓库根目录下，架构层下面再放模块。
7. 只被一个模块使用的工具函数和 SDK，放在该模块目录里。被同一服务里多个架构层共用的，在该服务下建 `utils/`。纯 Python、没有服务文件夹、且被多个架构层共用时，才在仓库根建 `utils/`。
8. 开始写代码之前，先确定模块清单和每个模块所在的目录。多模块项目把这份清单写进 `docs/architecture.md`。之后加模块，放进已经定好的目录，不要另起一套。
9. Python 项目的依赖包缺失时按需引用，必须具体到包名和版本号；装法与报告格式见 [SKILL.md](../SKILL.md)「跑 Python」与「requirements」两条。
10. 默认使用 conda 管理环境，怎么跑见 [SKILL.md](../SKILL.md)「跑 Python」。
11. Agent 自己后台起的测试进程：测完立刻停，不要常驻。用户已在跑的服务不要杀。
12. 已有项目的目录与本规范不一致时，先问用户再改。新文件跟所在项目现有结构走，不要按本规范去改邻居文件。已有 `docs/architecture.md` 时，新代码放到蓝图里已经写明的目录。
13. 根目录 `README.md` 的人读写法以邻域入口那份 README-FORMAT 为唯一事实源（定位 → 分步上手 → 怎么工作 / 接口 → 树形结构；禁止做成 `docs/` 索引）。本文只管仓目录与依赖落点，不另定一套 README 章节。

### 层和模块怎么切：照 OSI 七层模型那种分法

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
docs/                      # 架构、ADR、术语、待办方向（见第 5 条）
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
scripts/                   # 跑完就退出的入口（见第 3 条）
  backup/url_to_knowledge.py
tests/
ask_server.py              # 服务启动文件（多服务时按 服务名_server.py 命名）
embed_server.py
start_all.py               # 前后端一起起，只为少几步调试（见下节）
requirements.txt
main.py                    # 单服务项目才用这个命名
```

- 这棵树里 `offline/` `online/` 是**按数据流的阶段**分的架构层，不是按技术类型分的。别建 `models/` `services/` `handlers/` 这种横切目录当架构层。
- `embed/` 单独成层，是因为它被两条链共用、且是独立进程；被多层共用的东西才值得提出来当一层。
- 前端目录名随项目（`web/`、`frontend/` 都行），**关键是后端与前端在仓库里各自有一块完整地盘**，见「前后端同仓」。

## FastAPI 项目

用 FastAPI 时读本节。通用规则仍生效；**路由函数本身怎么写、请求与响应模型怎么定，见 [function.md](./function.md)**（与 `dataclass` 放在同一节讨论）。

1. 每个对外提供接口的模块目录里放 `router.py` 和 `schema.py`。

```plaintext
online/generate/
  __init__.py
  answer.py                # 本模块的业务实现
  router.py                # 对外接口：路径、方法、状态码
  schema.py                # 请求体定义（响应体按需）
```

- 不在仓库根再铺一套 `routers/<模块>/`——那样「这个接口属于哪一层」要跨目录对。
- 一个模块只有一个 `router.py`；接口多了先用注释分段，别按接口再拆文件。

2. `schema.py` 里**请求体必须定义成模型**；响应体允许直接 `return`——简单接口为了返回一个 dict 就再定义一个响应模型，调试时反而多一层要对照的东西。响应模型在「返回字段多、要被前端或外部依赖、要裁掉内部字段」时才是推荐做法。

3. 启动文件（`main.py` 或 `服务名_server.py`）只做四件事：创建应用、挂中间件、`include_router`、注册生命周期，并写明本服务的 host 和 port。业务实现放架构层或模块层。host 和 port 不写进 `config.yaml`（见通用规则 1），生产放 Dockerfile。

4. 进程级资源（连接池、向量库客户端、模型句柄）放 `lifespan`，路由只从应用状态取；每请求一份的资源（事务、临时文件）在依赖或路由内用 `with` 管住。示例：

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

5. 已有项目已经使用 `app.py`、`configs/`、`routers/` 的，跟现有结构走，先问再改。

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
