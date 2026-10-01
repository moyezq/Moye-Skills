# FastAPI 目录

项目使用 FastAPI 时读本文。通用规则仍生效。路由函数与 schema 字段怎么写见 `self-python-function`。

1. 每个对外提供接口的模块目录里，放 `router.py` 和 `schema.py`。不要在仓库根再铺一套 `routers/<模块>/`。
2. 启动文件（`main.py` 或 `服务名_server.py`）只创建应用、挂中间件、`include_router`、注册生命周期，并写明本服务的 host 和 port。业务实现放在架构层或模块层。host 和 port 不要写进 `config.yaml`。
3. 已有项目已经使用 `app.py`、`configs/`、`routers/` 的，跟现有结构走，先问再改。
