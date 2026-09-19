# 浏览器会话管理

并行跑多个隔离的浏览器会话，并可持久化状态。

## 命名浏览器会话

用 `-s` 隔离浏览器上下文：

```bash
# 浏览器 1：登录流程
playwright-cli -s=auth open https://app.example.com/login

# 浏览器 2：公开浏览（独立 cookies、storage）
playwright-cli -s=public open https://example.com

# 命令按浏览器会话隔离
playwright-cli -s=auth fill e1 "user@example.com"
playwright-cli -s=public snapshot
```

## 会话隔离属性

每个浏览器会话各自独立：
- Cookies
- LocalStorage / SessionStorage
- IndexedDB
- 缓存
- 浏览历史
- 打开的标签页

## 会话命令

```bash
# 列出全部浏览器会话
playwright-cli list

# 停止某个浏览器会话（关闭浏览器）
playwright-cli close                # 停止默认浏览器
playwright-cli -s=mysession close   # 停止命名浏览器

# 停止全部浏览器会话
playwright-cli close-all

# 强制杀掉全部守护进程（僵死/僵尸进程）
playwright-cli kill-all

# 删除浏览器会话用户数据（配置目录）
playwright-cli delete-data                # 删除默认浏览器数据
playwright-cli -s=mysession delete-data   # 删除命名浏览器数据
```

## 环境变量

用环境变量设默认会话名：

```bash
export PLAYWRIGHT_CLI_SESSION="mysession"
playwright-cli open example.com  # 自动使用 "mysession"
```

## 常见模式

### 并发抓取

```bash
#!/bin/bash
# 并发抓多个站点

# 启动全部浏览器
playwright-cli -s=site1 open https://site1.com &
playwright-cli -s=site2 open https://site2.com &
playwright-cli -s=site3 open https://site3.com &
wait

# 分别拍快照
playwright-cli -s=site1 snapshot
playwright-cli -s=site2 snapshot
playwright-cli -s=site3 snapshot

# 清理
playwright-cli close-all
```

### A/B 测试会话

```bash
# 测不同用户体验
playwright-cli -s=variant-a open "https://app.com?variant=a"
playwright-cli -s=variant-b open "https://app.com?variant=b"

# 对比
playwright-cli -s=variant-a screenshot
playwright-cli -s=variant-b screenshot
```

### 持久化配置

默认浏览器配置只在内存。在 `open` 时加 `--persistent` 可把配置落到磁盘：

```bash
# 使用持久化配置（自动生成路径）
playwright-cli open https://example.com --persistent

# 使用自定义目录的持久化配置
playwright-cli open https://example.com --profile=/path/to/profile
```

## Attach 到已运行的浏览器

用 `attach` 连接已在运行的浏览器，而不是新开一个。

### 按渠道名 Attach

按渠道名连接到已运行的 Chrome 或 Edge。目标浏览器须开启远程调试——在目标浏览器打开 `chrome://inspect/#remote-debugging`，勾选 "Allow remote debugging for this browser instance"。

```bash
# Attach 到 Chrome
playwright-cli attach --cdp=chrome

# Attach 到 Chrome Canary
playwright-cli attach --cdp=chrome-canary

# Attach 到 Microsoft Edge
playwright-cli attach --cdp=msedge

# Attach 到 Edge Dev
playwright-cli attach --cdp=msedge-dev
```

支持的渠道：`chrome`、`chrome-beta`、`chrome-dev`、`chrome-canary`、`msedge`、`msedge-beta`、`msedge-dev`、`msedge-canary`。

未提供 `--session` 时，会话名取渠道名（例如 `--cdp=msedge` 会创建名为 `msedge` 的会话），这样并行 attach Chrome 与 Edge 不会撞在 `default` 上。可用 `--session=<name>` 覆盖。

### 经 CDP 端点 Attach

连接到暴露 Chrome DevTools Protocol 端点的浏览器：

```bash
playwright-cli attach --cdp=http://localhost:9222
```

### 经浏览器扩展 Attach

连接到已安装 Playwright 扩展的浏览器：

```bash
playwright-cli attach --extension
```

### Detach

拆除 attach 会话，不影响外部浏览器：

```bash
# 断开默认 attach 会话
playwright-cli detach

# 断开指定 attach 会话
playwright-cli -s=msedge detach
```

`detach` 只对经 `attach` 创建的会话有效。经 `open` 创建的会话用 `close`。

## 默认浏览器会话

省略 `-s` 时，命令使用默认浏览器会话：

```bash
# 这些用的是同一个默认会话
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli close  # 停止默认浏览器
```

## 会话配置

打开时可为会话指定配置：

```bash
# 用配置文件打开
playwright-cli open https://example.com --config=.playwright/my-cli.json

# 指定浏览器打开
playwright-cli open https://example.com --browser=firefox

# 有界面模式打开
playwright-cli open https://example.com --headed

# 带持久化配置打开
playwright-cli open https://example.com --persistent
```

## 最佳实践

### 1. 给会话起有语义的名字

```bash
# 好：目的清晰
playwright-cli -s=github-auth open https://github.com
playwright-cli -s=docs-scrape open https://docs.example.com

# 避免：泛化名字
playwright-cli -s=s1 open https://github.com
```

### 2. 用完务必清理

```bash
# 用完后关掉浏览器
playwright-cli -s=auth close
playwright-cli -s=scrape close

# 或一次关掉全部
playwright-cli close-all

# 浏览器无响应或残留僵尸进程时
playwright-cli kill-all
```

### 3. 删除陈旧浏览器数据

```bash
# 删掉旧会话数据腾磁盘
playwright-cli -s=oldsession delete-data
```
