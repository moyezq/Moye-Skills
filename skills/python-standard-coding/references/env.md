# 环境与依赖

Python 项目用什么管环境、怎么跑、缺包怎么办、依赖写在哪。conda 与 uv 两种都成立，按项目与场景选，不搞统一。

完成标准：新加的依赖已写进项目现有的那份清单并钉了版本；本地跑法与项目现有方式一致；没有为了「统一」把项目迁到另一种管理器。

## 何时用

**用**：新建项目定环境管理器；第一次为任务跑 Python；给已有项目加依赖；某条安装路径装不上、要换一种方式时。

**不用**：只改函数内部，不动环境与依赖。

## 先沿用，再选

项目原来用什么就接着用什么；没有既有要求时沿用宿主已有的，不为了统一增加工作量。真要从零选时，按下面两节。

## 什么时候 uv 更好

1. **最小服务、快速验证**：`uv run python serve_xxx.py` 起服务、`uv run python probe_xxx.py` 打它，目录自带 `.venv`，不碰宿主环境。
2. **开源、要别人在别的机器上部署**：`pyproject.toml` + `uv.lock` 把版本钉死，clone 下来一条 `uv sync` 装齐。

## 什么时候 conda 更好

- 脚本级的一次性验证，宿主已有 conda 环境，直接复用，不另造环境。
- 已有环境里装着重建代价大的东西（某个 CUDA 版本、某个已经调通的 torch），重建远不如复用。

## 怎么跑

- 每个终端两行，一行管环境、一行管运行；不用 `conda run -n`

```text
# ✅ 正确
conda activate base
python main.py

# ❌ 错误
conda run -n base python main.py
```

- 选了 uv 的项目用 `uv run python …`
- AI 自己在非交互 shell 里跑时不依赖 `conda activate`：用解释器绝对路径 `<envs>/<环境>/python.exe -m pytest …`
- 装包走已激活环境里的 `pip`，不信 PATH 上那个

## 缺包

- 直接 `import`，缺了把五项报给用户：环境名 / 入口 / 包名 / 报错 / 安装命令。不预检第三方包、不自动 `pip install`

```python
# ✅ 正确
import pandas          # ModuleNotFoundError → 报上面五项

# ❌ 错误
if importlib.util.find_spec("pandas") is None:
    subprocess.run(["pip", "install", "pandas"])
```

```powershell
conda activate <环境>
pip install <包>
```

- 用户说装再执行；对齐阶段说过「允许多装某包」的视为已授权
- 不跑 `pip list` 探测

## 依赖写在哪

- 只写运行入口真正 `import` 到的第三方包，每行 `包名==版本`；不抄 `pip freeze` 的全部结果

```text
# ✅ 正确
numpy==2.1.0
pandas==2.2.2

# ❌ 错误
numpy==2.1.0
pytz==2024.1        # numpy 拉的
six==1.16.0
```

- 标准库能覆盖的不装；装完用 `pip show <包>` 读发行名与 Version 写进去
- uv 项目写 `pyproject.toml` + `uv.lock`，同样只声明直接依赖
