---
name: self-python-project
description: 个人 Python 项目里文件放哪、目录怎么分层，以及根目录 README 按哪几块写。新建项目、加模块、设计目录、整理已有仓、改目录、写或改 README 时查阅（只说整理也要读）。动态配置在 conf/base.py；host/port 写在启动文件；第三方对接和密钥在 .env，不要写进 config.yaml。层/模块测试在 scripts/，启动文件在仓库根。FastAPI 路由文件、前后端同仓目录按条件读本 skill 的 references。单文件脚本见 self-python-script；函数怎么写见 self-python-function；风格与怎么跑见 self-python-style；项目文档何时建见 project-docs。命令：/self-python-project
---

# Python 项目结构与设计规范

管 **个人 Python 项目里文件放哪、目录怎么分层、根目录 README 按哪几块写**。
- 风格与怎么跑见 `self-python-style`；
- 函数怎么写见 `self-python-function`；
- 单文件分阶段脚本、以及入口脚本文件头怎么写，见 `self-python-script`；
- 项目文档何时建、读、改见 `project-docs`。

完成标准：新建或改目录时，通用规则每条都套上；写或改 README 时按第 13 条四块写；命中 FastAPI 或前后端同仓时已读对应 reference；单文件分阶段脚本没有套本文件的目录。

带「何时读」的 reference 只在条件满足时读。

## 何时用

**用**：新建项目、加模块、设计目录、整理已有仓、改目录、写或改 README。

**不用**：单文件分阶段脚本（见 `self-python-script`）。只改函数内部、不改目录。

---

## 通用规则

1. 项目的配置统一放在根目录的 `conf` 文件夹中，并按下面分类，不要混放。
   - 随运行环境变化、要从本机推算的值，放在 `conf/base.py`。例如项目根目录 ROOT：用 `Path(__file__).resolve()` 推算，不要把盘符写进 yaml。把仓库根加入 `sys.path` 也写在这里。启动文件和脚本引用这里的 ROOT，不要每个文件再写一遍。
   - 本服务的 host、port 直接写在对应的 `main.py` 或 `服务名_server.py` 里。本地不常改；生产放 Dockerfile。不要写进 `config.yaml`。
   - `conf/config.yaml` 只放各环境相同、属于本项目自己的公共常量，例如相对数据目录、模型目录名。不要放 ROOT、host、port、第三方地址、密钥。
2. 第三方对接配置和隐私配置统一放在根目录 `.env`；模板放根目录 `.env_example`。
   - 第三方对接：外仓 HTTP 地址这类对接参数，例如 `anyurl2text_url`。
   - 隐私配置：API Key、Token、填了密钥的别人家 `.env` 路径。不要写进 `config.yaml`，也不要在 yaml 里指向另一份带密钥的 `.env`。
3. 项目的层/模块测试文件，统一放在根目录 `scripts` 中。跑完就退出的入库、评测、探测也放这里。例如：RAG 从文件到进入向量数据，由一个 `scripts/ingest.py` 来测试。这些入口脚本的文件头怎么写见 `self-python-script`。
4. 如果是单服务的项目，根目录启动文件统一使用 `main.py` 命名；如果是多服务项目，根目录放多个服务的启动文件，以 `服务名_server.py` 命名。启动文件只负责启动服务、写明 host 和 port、挂路由和生命周期。业务实现放在架构层或模块层目录里。不要用 `python 子目录/xxx.py` 启动服务。同一个进程不要在包内再留一份 `__main__`。
5. 项目的设计文档、架构图、项目关键架构和技术决策（ADR）统一放在 `docs` 中。写法见 `project-docs`。
6. 没有前端时，不建 `frontend/` 和 `backend/`。架构层直接放在仓库根目录下，架构层下面再放模块。
7. 只被一个模块使用的工具函数和 SDK，放在该模块目录里。被同一服务里多个架构层共用的，在该服务下建 `utils/`。纯 Python、没有服务文件夹、且被多个架构层共用时，才在仓库根建 `utils/`。
8. 开始写代码之前，先确定模块清单和每个模块所在的目录。多模块项目把这份清单写进 `docs/architecture.md`。之后加模块，放进已经定好的目录，不要另起一套。
9. Python 项目的依赖包缺失时按需引用，必须具体到包名和版本号，然后告知用户安装命令，确定可用后写入根目录 `requirements.txt`。探测环境和安装步骤见 `self-python-style`。
10. 默认使用 conda 管理环境。启动项目时默认已处在对应环境中，不要 `conda run -n`。告诉用户怎么跑时，写成 `conda activate` 再 `python`。
11. Agent 自己后台起的测试进程：测完立刻停，不要常驻。用户已在跑的服务不要杀。
12. 已有项目的目录与本规范不一致时，先问用户再改。新文件跟所在项目现有结构走，不要按本规范去改邻居文件。已有 `docs/architecture.md` 时，新代码放到蓝图里已经写明的目录。
13. 根目录 `README.md` 按下面四块写。每块分开，不要把不同内容揉成一段。什么时候建 README 见 `project-docs`。
    - **系统基础信息**：第一行是系统名称。名称下面直接写系统做什么，不用再分标题。然后列设计原型：每条一个通俗、准确的标签加链接（例如架构、术语、视觉、技术决策）。有文件才链，没有的条目不写。
    - **生产、准备、启动、依赖**：生产信息写接口文档地址（未部署到生产则写本地地址）和 GitHub 地址（没有写「无」）。准备工作写在启动方式之前，只写启动前必须做的最少步骤；源文件和产物会变，不要把具体文件名、只跑哪一份、字段怎么抽钉死在 README。当前实现可以写「当前用 xx」，给以后换方案留空间。启动方式：有几个长驻服务就写几个，步骤要最简单直观。系统依赖写清本项目依赖谁、要什么密钥；本系统还向其它系统提供服务时也要写，没有则不写。
    - **项目结构**：关键目录和文件的树，每个写一句功能；再用短段落说明层和模块各自做什么。
    - **使用说明**（放在项目结构后面）：当前设计下数据怎么进系统（输入长什么样、输出长什么样、跑哪条命令）；主功能的简单测试（可复制的输入、步骤、预期结果；连续对话写明同一会话、不要刷新）；`scripts/` 里哪个文件测哪一层或哪条流程，没有单独测试文件的如实写，不要编。
    - 不要写进 README：还没验证、还要对照实验的方案（写进 `TODO.md` 等计划：目前还未验证出最准确、稳定的方向，当前暂定 xx，候选有哪些）；会随需求经常变的前端交互边界（视觉见 `DESIGN.md`，明确不做见 `docs/architecture.md`）；未定的实验入口；读者看不懂的生僻叫法。

没有前端时，根目录看起来像这样：

```plaintext
README.md
conf/base.py
conf/config.yaml
.env
.env_example
docs/
scripts/
offline/
embed/
main.py
embed_server.py
requirements.txt
```

## 按条件再读

- 项目使用 FastAPI：读 [references/fastapi.md](./references/fastapi.md)。路由处理函数怎么写见 `self-python-function`。
- 前后端分离且归在同一目录：读 [references/fullstack.md](./references/fullstack.md)。
