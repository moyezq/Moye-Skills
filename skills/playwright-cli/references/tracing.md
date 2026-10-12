# Tracing

录制详细执行轨迹，用于调试与分析。轨迹含 DOM 快照、截图、网络活动与控制台日志。

## 基础用法

```bash
# 开始录制 trace
playwright-cli tracing-start

# 执行操作
playwright-cli open https://example.com
playwright-cli click e1
playwright-cli fill e2 "test"

# 停止录制 trace
playwright-cli tracing-stop
```

## Trace 产出文件

开始 tracing 后，Playwright 会创建 `traces/` 目录及若干文件：

### `trace-{timestamp}.trace`

**动作日志** — 主 trace 文件，包含：
- 执行过的每个动作（点击、填充、导航）
- 每个动作前后的 DOM 快照
- 每一步的截图
- 时序信息
- 控制台消息
- 源码位置

### `trace-{timestamp}.network`

**网络日志** — 完整网络活动：
- 全部 HTTP 请求与响应
- 请求头与请求体
- 响应头与响应体
- 时序（DNS、连接、TLS、TTFB、下载）
- 资源大小
- 失败请求与错误

### `resources/`

**资源目录** — 缓存资源：
- 图片、字体、样式表、脚本
- 用于回放的响应体
- 重建页面状态所需资源

## Trace 捕获内容

| 类别 | 细节 |
|------|------|
| **Actions** | 点击、填充、悬停、键盘输入、导航 |
| **DOM** | 每个动作前后的完整 DOM 快照 |
| **Screenshots** | 每一步的视觉状态 |
| **Network** | 全部请求、响应、头、体、时序 |
| **Console** | 全部 console.log / warn / error |
| **Timing** | 每个操作的精确时序 |

## 使用场景

### 调试失败动作

```bash
playwright-cli tracing-start
playwright-cli open https://app.example.com

# 这次点击失败——为什么？
playwright-cli click e5

playwright-cli tracing-stop
# 打开 trace，查看尝试点击时的 DOM 状态
```

### 分析性能

```bash
playwright-cli tracing-start
playwright-cli open https://slow-site.com
playwright-cli tracing-stop

# 查看网络瀑布图，定位慢资源
```

### 留存证据

```bash
# 录完整用户流程，作文档用
playwright-cli tracing-start

playwright-cli open https://app.example.com/checkout
playwright-cli fill e1 "4111111111111111"
playwright-cli fill e2 "12/25"
playwright-cli fill e3 "123"
playwright-cli click e4

playwright-cli tracing-stop
# Trace 展示精确事件序列
```

## Trace vs 视频 vs 截图

| 特性 | Trace | 视频 | 截图 |
|------|-------|------|------|
| **格式** | .trace 文件 | .webm 视频 | .png/.jpeg 图片 |
| **DOM 检查** | 有 | 无 | 无 |
| **网络细节** | 有 | 无 | 无 |
| **逐步回放** | 有 | 连续画面 | 单帧 |
| **文件大小** | 中等 | 大 | 小 |
| **最适合** | 调试 | 演示 | 快速抓取 |

## 最佳实践

### 1. 在问题出现前就开始 Tracing

```bash
# 录整段流程，不要只录失败那一步
playwright-cli tracing-start
playwright-cli open https://example.com
# ... 通向问题的全部步骤 ...
playwright-cli tracing-stop
```

### 2. 清理旧 Trace

Trace 会占不少磁盘：

```bash
# 删除 7 天前的 traces
find .playwright-cli/traces -mtime +7 -delete
```

## 限制

- Tracing 会给自动化带来开销
- 大 trace 会占较多磁盘
- 部分动态内容可能无法完美回放
