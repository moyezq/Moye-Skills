---
name: self-python-project
description: 项目组织与案例归档。整理项目、改目录、归档案例、组织 Production/Model-Server、嫌模块拆太多时查阅（只说整理也要读）。按条件选单文件脚本 / 流水线类 / FastAPI 小服务，不要混套。函数内部见 self-python-function；风格与怎么跑见 self-python-style；脚本切步见 self-python-script；外仓进笔记见 self-notes-read。
---

# 项目组织与案例归档

管 **目录怎么摆、案例怎么归档、三种落地形态选哪个**。函数内部见 `self-python-function`；风格与怎么跑见 `self-python-style`；脚本切步见 `self-python-script`；12 条判断见 `self-code-principles`。

完成标准：形态三选一不混套；产物进 `data/`；短链路不拆薄文件瀑布；已有能跑的项目先问再改。

带「何时使用」的条目只在条件满足时套，不强行推广到所有项目。

## 何时用

**用**：整理项目、改目录、归档案例、组织 `Production/` / `Model-Server/`、嫌拆太多。

脚本切步、函数内部分别再加读对应 skill，不替代本文件。

## 已有项目

发现已有项目与原则明显对不上时，先问再改（判断见兜底原则 3、7、11）。包括但不限于：改目录形态、RPC 改 REST、换配置体系、引入 Alembic / 领域分包 / 全局基类、全量格式化。

新文件跟所在项目现有结构走，不要按本 skill 去「纠正」邻居文件。

## 三种落地形态

| 形态 | 适用 | 写法看哪 |
|------|------|----------|
| 单文件分阶段脚本 | 搜索 → 详情 → 下载等，一个 `.py` 能跑完 | `self-python-script` |
| 流水线类（多文件案例） | 加载 → 处理 → 输出，某步失败要停后续；步骤在类或 `utils/` 里 | 类内部见 `self-python-function` |
| FastAPI 小服务 | `Production/`、`Model-Server/` 这类单一 HTTP 服务 | 本文件目录约定；路由函数见 `self-python-function` |

**可安装库不是第四种形态**：只有要 `pip install`、要发版本时才用 `src/` + `pyproject.toml`。小服务、案例、分阶段脚本用上面三种，保持本文件的目录。

**流水线类不适用**：工具函数集、单一 HTTP 服务、步骤边界模糊的流程、其实一个文件就写得完的脚本。

**已有 `utils/` 的多文件流水线**：阶段逻辑仍在 `utils/`，入口每阶段一行调用 + 一行注释（做什么、产出路径）。不要只调一个黑盒 `run()` / `fetch_all()` 却不让人看见步骤。类的 `run()` 可以保留，那是编排，见 `self-python-function`。

## FastAPI 小服务目录

**适用**：`Production/`、`Model-Server/` 这类单一 HTTP 服务（SQL 网关、任务入口、ASR、OSS、超时提醒等）。

**不适用**：多域单体、工具函数集、分阶段爬虫脚本。

沿用现有形态：入口在仓库根下的 `app.py` / `main.py`，不要改成 `src/<pkg>/`。也不要套多域单体模板（`src/auth`、`src/posts` 各带一套 router/schemas/models/service）：

```plaintext
app.py                 # 或 main.py：FastAPI 入口、中间件、include_router
configs/               # 环境、Apollo/dotenv、日志、DB、监控
routers/<模块>/        # router.py + schema.py
utils/                 # 非路由的工具与 SDK
```

- 配置跟项目已有层（Apollo + dotenv + Dev/Qas/Prd），不换成按域拆的 `pydantic BaseSettings`。
- 内部任务接口保持 RPC（如 `POST /process`、`POST /execute_sql`）；资源查询类可按现有 `plan_book` / `asr-kit` 写 REST。不要为了 REST 去改能跑的任务入口。
- 鉴权、SkyWalking、Prometheus、lifespan 连接池、Dramatiq/队列以当前服务为准，不按外部清单增删。
- 不引入全局 `CustomModel` 统一序列化；不补 Alembic、pytest 异步 TestClient、全仓库 ruff format。
- 仅当 `/docs` / `openapi.json` 能被公网直接访问时，才建议关掉；对内网联调保持现状，先问再改。
- 独立演示型、无 Apollo 分层时，可用单文件 `config/settings.py` 硬编码。

### 先写通，再抽文件

**适用**：单一业务链路的小 HTTP 服务（如消息入站 → 分流 → 缓存 → 轮询 → 提醒），代码量不大、步骤主要被串联调用。

默认把同一条短流水线写在 **一个业务文件**（如 `core/service.py`）；`app.py` 只做路由与 lifespan。不要为「目录好看」按阶段建空分包，也不要每个步骤各拆一个薄 `*.py`。

仅当规则在 **两处以上真正复用**，或工具相对独立（表情过滤、DB 初始化、外部 SDK 适配）时再单拆文件。用户要求「合并 / 少拆文件」时：合并后删除已无入口的拆分文件与死对照代码。

改字段名、类名、路由、配置常量之前先钉死契约：以 `data/` 里的样例、`scheme`、联调脚本里真实 POST body 为准，整链统一。删模块、改配置路径后提醒重启，见会话索引。

## 案例归档与脱敏

- 样例 JSON（`data/*.json` 或 `data/sample_*.json`）替代运行时查库；可保留 `sql/create_table.sql`。
- 去除内网地址、发群、OSS 等生产环节。
- **运行产物写案例/服务同级 `data/`**。不要平行再开 `output/`；若已有，迁入 `data/` 后删空目录。`data/` 下若只有一个无业务意义的子目录，内容上移一级。单文件脚本的输入输出目录见 `self-python-script`。
- **笔记库 `cases/`**：目录名与案例内文件名优先英文（`company_background`、`01_case.md`）；标题可用中文括注。

## 代码定位

按优先级由窄到宽：README / 子目录说明 / `_meta/` / 用户 @ 的路径 → 锁定目录后 grep → 语义搜索指定 `target_directories` → 无结果再扩大。不要全仓库无范围 grep、批量 Read 无关文件。

大工具库可维护关键词→路径索引 JSON；非强制。

## 多案例归档目录

**适用**：多案例可复用代码合集。

顶层按能力分：`Scripts/`、`Spyder/`、`Production/`、`Model-Server/`、`Automation/`。第三方镜像单独目录。子项目 README 写做什么、怎么用、注意什么；敏感信息用占位或 `.env`。

## 文档边界

说明用 `.md` 见会话索引。库/工具知识写入 `笔记库` 既有编号文档，不要在案例旁另建 `docs/` 堆官方全文；外仓收脚本按主题并进库文，不要用「工具链案例」顶替。写法和落位见 `self-notes-read`。
