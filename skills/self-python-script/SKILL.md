---
name: self-python-script
description: 单文件分阶段 Python 脚本。目标已定、实现落进一个 .py、能按真实数据跳写流程时查阅；写爬虫、批处理、离线流水线、探测接口、说「写个脚本」时也查阅（没提 step 也要读）。风格与怎么跑见 self-python-style；函数内部见 self-python-function；有对照开源时抽协议见 笔记库/05-Spyder/10_从对照项目还原协议.md；多文件目录见 self-python-project。
---

# 单文件分阶段 Python 脚本

只管 **一个 `.py` 里怎么把已定目标写成可顺着读的流程**。风格、字段、运行参数、print 与 logger、第一次怎么跑见 `self-python-style`。抽不抽函数见 `self-python-function`。用户给了开源 App / 插件当对照时，协议怎么抽见 `<工作目录>\笔记库\05-Spyder\10_从对照项目还原协议.md`。多文件案例与 FastAPI 目录见 `self-python-project`。

完成标准：每个数据跳一个 `stepN`；`__main__` 只编排、且在文件最末尾；参数硬编码；输入在 `data/` 或 `data/source/`，产出在 `data/result/`，分步文件名与 `stepN` 同号。

## 何时用

**用**：目标已经说清（下哪本书、处理哪份 JSON、打哪条接口）；实现可以放进一个 `.py`；中间有真实的数据跳（请求 → 取字段 → 下一跳）。有对照开源项目时先读那篇还原协议笔记，再按本文件切 `stepN`。

**不用**：FastAPI `app.py` / 小服务；纯工具函数集（没有「跑一遍」的流程）；真·一步脚本（读文件、转一下、结束）；多文件流水线或带 `utils/` 的案例服务（入口形态见 `self-python-project`）。

---

## 脚本入口

- 运行参数放文件顶部常量区或 `__main__` 第一行（不用 argparse 见 `self-python-style`）。
- `if __name__ == "__main__"` 只按阶段调用 `stepN_...`，不解析参数、不写业务细节。

```python
if __name__ == "__main__":
    COMIC_NAME = "书名"
    # 阶段0：network2 → api_host
    api_host = step0_resolve_api_host()
    # 阶段1：搜索 → path_word
    hit = step1_search_comic(api_host, COMIC_NAME)
    # 阶段2：comic2 → 简介、默认分组话数
    results = step2_fetch_comic_detail(api_host, hit["path_word"])
```

- 每阶段一行注释（做什么、产出路径）+ 一行调用。不要再包一层 `run()` / `fetch_all()` 把步骤藏进去。
- 步骤函数就写在本文件，按 `step0`、`step1`… 排。不要为了对齐「逻辑必须在 utils」而拆文件。

## 按真实数据跳切步骤

不要按「感觉上的函数粒度」切。一跳 = 一次请求或一次明确的数据变换，加上取字段、打印、本步产出。

- **一步一个 `stepN_xxx`**：一个 def 做完这一跳。函数在文件里按 0、1、2… 顺序排。
- **步骤内按执行顺序写**：先请求、再取字段、再打印/落盘。读一个 step 就能看懂这一跳。
- **步骤内注释写清数据流**：哪个 URL、吃上一跳哪个字段、吐给下一跳什么。`#` 怎么写见 `self-python-style`。
- **日志前缀与函数同号**：`step2_...` 打印 `[阶段2]`，不要阶段号和函数号错位。

协议还没摸清时，先写 **探测脚本**（一个文件打一个 URL），不要一上来写总控。落盘见下节。

## 脚本里什么算无效封装

抽函数的一般规则见 `self-python-function`（薄包装）。脚本里另外这几条会把流程写难看懂：

- 把同一步拆成 `fetch_x` + `download_one_x` + `download_selected_x`，主流程要跳三次才能看完
- `max_workers=1` 的线程池包一层 for 循环
- 同一步骤里若线程池需要 callable，用 **步骤内嵌套 def**，不要提升成模块级工具

可以留：被 **两个以上步骤** 真正调用、且规则固定的协议细节（共用 HMAC GET、设备指纹、统一的 HTTP 非 200 报错）。

## data/ 输入与产出

这一节是脚本级输入输出的**单一事实源**。多文件案例与 FastAPI 小服务怎么摆 `data/`，见 `self-python-project`（那里只指向本节，不另起一套子目录名）。

脚本同级建 `data/`。不要平行再开 `output/` 或 `analyse/output/`。

**输入**

- 只有一份源文件：直接放 `data/<文件>`。
- 多份源文件：放 `data/source/`。

**产出**

- 一律写 `data/result/`。
- 分阶段脚本每步若落盘：文件名 `stepN_<含义>.<ext>`，`N` 与函数 `stepN_...` 同号，print 写出的路径。
- 一步脚本只有一份结果：`data/result/<含义>.<ext>`。

打开 `data/result/` 应能看出哪一步写出了哪个文件。没落盘的步骤不必硬造空文件。

## 编号只对应一条有序序列

使用者按序号选择的列表（第 N 话、第 N 条）必须对应 **一条有序序列**。站点上并行的分类（默认话 vs 单行本 / 番外）不要加总后再从 1 编号。

## 日志

| 场景 | 示例 |
|------|------|
| 大步骤 | `[阶段2] 已写入 data/result/step2_detail.json` |
| 循环 | `[3/120] 条目名` |
| 结论 | `问 → 答 → ... \| 结论: xxx` |

用 print 还是 logger 见 `self-python-style`。批量 HTTP 关闭 per-request 调试；循环内不 dump 完整 JSON。

## 批处理

循环处理多条时，一笔失败记入失败列表并继续下一条；整批结束打印成功数/失败数，并列出失败项与原因。
