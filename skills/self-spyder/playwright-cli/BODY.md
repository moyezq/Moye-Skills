---
name: playwright-cli
description: 用 playwright-cli 自动化浏览器交互、测网页、调试/生成 Playwright 测试。用户提到浏览器自动化、网页点击填表、页面快照、Playwright CLI、UI 走查、录屏/tracing、请求 mock、或要用 npx playwright test --debug=cli 时必须使用本 skill。整站复刻/仿站走 self-frontend。
allowed-tools: Bash(playwright-cli:*) Bash(npx:*) Bash(npm:*)
---

# 用 playwright-cli 做浏览器自动化

## 快速开始

```bash
# 打开新浏览器
playwright-cli open
# 导航到页面
playwright-cli goto https://playwright.dev
# 用快照里的 ref 与页面交互
playwright-cli click e15
playwright-cli type "page.click"
playwright-cli press Enter
# 截图（少用；更常见的是 snapshot）
playwright-cli screenshot
# 关闭浏览器
playwright-cli close
```

## 命令

### 核心

```bash
playwright-cli open
# 打开并立刻导航
playwright-cli open https://example.com/
playwright-cli goto https://playwright.dev
playwright-cli type "search query"
playwright-cli click e3
playwright-cli dblclick e7
# --submit 在填充后按 Enter
playwright-cli fill e5 "user@example.com"  --submit
playwright-cli drag e2 e8
# 把文件或数据拖放到元素上（来自页面外部）
playwright-cli drop e4 --path=./image.png
playwright-cli drop e4 --data="text/plain=hello world"
playwright-cli hover e4
playwright-cli select e9 "option-value"
playwright-cli upload ./document.pdf
playwright-cli check e12
playwright-cli uncheck e12
playwright-cli snapshot
# 在快照中搜索文本或正则，返回匹配节点及上下文
playwright-cli find "Sign in"
playwright-cli find --regex "Sign (in|up)"
# 用斜杠包住正则可加标志，例如 /i 表示忽略大小写
playwright-cli find --regex "/sign (in|up)/i"
playwright-cli eval "document.title"
playwright-cli eval "el => el.textContent" e5
# 获取快照里看不到的 id、class 或任意属性
playwright-cli eval "el => el.id" e5
playwright-cli eval "el => el.getAttribute('data-testid')" e5
playwright-cli dialog-accept
playwright-cli dialog-accept "confirmation text"
playwright-cli dialog-dismiss
playwright-cli resize 1920 1080
playwright-cli close
```

### 导航

```bash
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
```

### 键盘

```bash
playwright-cli press Enter
playwright-cli press ArrowDown
playwright-cli keydown Shift
playwright-cli keyup Shift
```

### 鼠标

```bash
playwright-cli mousemove 150 300
playwright-cli mousedown
playwright-cli mousedown right
playwright-cli mouseup
playwright-cli mouseup right
playwright-cli mousewheel 0 100
```

### 另存为

```bash
playwright-cli screenshot
playwright-cli screenshot e5
playwright-cli screenshot --filename=page.png
playwright-cli screenshot --hires
playwright-cli pdf --filename=page.pdf
```

### 标签页

```bash
playwright-cli tab-list
playwright-cli tab-new
playwright-cli tab-new https://example.com/page
playwright-cli tab-close
playwright-cli tab-close 2
playwright-cli tab-select 0
```

### 存储

```bash
playwright-cli state-save
playwright-cli state-save auth.json
playwright-cli state-load auth.json

# Cookies
playwright-cli cookie-list
playwright-cli cookie-list --domain=example.com
playwright-cli cookie-get session_id
playwright-cli cookie-set session_id abc123
playwright-cli cookie-set session_id abc123 --domain=example.com --httpOnly --secure
playwright-cli cookie-delete session_id
playwright-cli cookie-clear

# LocalStorage
playwright-cli localstorage-list
playwright-cli localstorage-get theme
playwright-cli localstorage-set theme dark
playwright-cli localstorage-delete theme
playwright-cli localstorage-clear

# SessionStorage
playwright-cli sessionstorage-list
playwright-cli sessionstorage-get step
playwright-cli sessionstorage-set step 3
playwright-cli sessionstorage-delete step
playwright-cli sessionstorage-clear
```

### 网络

```bash
playwright-cli route "**/*.jpg" --status=404
playwright-cli route "https://api.example.com/**" --body='{"mock": true}'
playwright-cli route-list
playwright-cli unroute "**/*.jpg"
playwright-cli unroute
```

### DevTools

```bash
playwright-cli console
playwright-cli console warning
playwright-cli requests
playwright-cli request 5
playwright-cli run-code "async page => await page.context().grantPermissions(['geolocation'])"
playwright-cli run-code --filename=script.js
playwright-cli tracing-start
playwright-cli tracing-stop
playwright-cli video-start video.webm
playwright-cli video-chapter "Chapter Title" --description="Details" --duration=2000
playwright-cli video-stop

# 给后续每个动作（click、type 等）加标注：标出动作名并高亮目标
playwright-cli video-show-actions --duration=600 --position=top-right
playwright-cli video-hide-actions

# 打开仪表盘做 UI 评审 / 设计反馈——用户在页面上标注后，你收到带标注截图、快照和备注
playwright-cli show --annotate

# 根据元素的 ref 或选择器生成 Playwright locator
playwright-cli generate-locator e5 --raw

# 给元素加持久高亮覆盖层，可选自定义样式
playwright-cli highlight e5
playwright-cli highlight e5 --style="outline: 3px dashed red"
# 隐藏单个元素高亮；不传目标则隐藏页面上全部高亮
playwright-cli highlight e5 --hide
playwright-cli highlight --hide
```

## 原始输出

全局选项 `--raw` 会去掉页面状态、生成代码、快照等段落，只返回结果值，便于把输出管道到其它工具。本身无输出的命令在 `--raw` 下也不返回内容。

```bash
playwright-cli --raw eval "JSON.stringify(performance.timing)" | jq '.loadEventEnd - .navigationStart'
playwright-cli --raw eval "JSON.stringify([...document.querySelectorAll('a')].map(a => a.href))" > links.json
playwright-cli --raw snapshot > before.yml
playwright-cli click e5
playwright-cli --raw snapshot > after.yml
diff before.yml after.yml
TOKEN=$(playwright-cli --raw cookie-get session_id)
playwright-cli --raw localstorage-get theme
```

需要把每条回复包成 JSON 时，传 `--json`：

```bash
playwright-cli list --json
```

## open 参数

```bash
# 创建会话时指定浏览器
playwright-cli open --browser=chrome
playwright-cli open --browser=firefox
playwright-cli open --browser=webkit
playwright-cli open --browser=msedge

# 模拟通用移动设备（Chromium 用 Pixel 10，WebKit 用 iPhone 17）。
# 移动布局可接受时优先用这个：移动页通常更轻，快照更小、更省。
playwright-cli open --mobile
playwright-cli open --device="iPhone 15"

# 使用持久化配置（默认配置在内存中）
playwright-cli open --persistent
# 使用自定义目录的持久化配置
playwright-cli open --profile=/path/to/profile

# 通过 Playwright 扩展连接到浏览器
playwright-cli attach --extension=chrome

# 按渠道名连接到已运行的 Chrome 或 Edge
playwright-cli attach --cdp=chrome
playwright-cli attach --cdp=msedge

# 通过 CDP 端点连接已运行的浏览器
playwright-cli attach --cdp=http://localhost:9222

# 用配置文件启动
playwright-cli open --config=my-config.json

# 关闭浏览器
playwright-cli close
# 从已 attach 的浏览器断开（外部浏览器继续运行）
playwright-cli -s=msedge detach
# 删除默认会话的用户数据
playwright-cli delete-data
```

## Windows 上带 `&` 的 URL

在 Windows 上，`cmd.exe` 和 PowerShell 会把 `&` 当成命令分隔符，带多个查询参数的 URL 会在传到 `playwright-cli` 之前被截断。在 `cmd.exe` 里用 `^&` 转义 `&`，或在 PowerShell 里用 `--%`：

```batch
playwright-cli goto "https://example.com/?a=1^&b=2"
```

```powershell
playwright-cli --% goto "https://example.com/?a=1&b=2"
```

## 快照（Snapshots）

每条命令执行后，playwright-cli 都会给出当前浏览器状态的快照。

```bash
> playwright-cli goto https://example.com
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
[Snapshot](.playwright-cli/page-2026-02-14T19-22-42-679Z.yml)
```

也可随时用 `playwright-cli snapshot` 主动拍快照。下面选项可按需组合。

```bash
# 默认：保存到带时间戳文件名的文件
playwright-cli snapshot

# 保存到指定文件；快照本身是工作流结果的一部分时用
playwright-cli snapshot --filename=after-click.yaml

# 只快照某个元素，而不是整页
playwright-cli snapshot "#main"

# 限制快照深度以提高效率，之后再拍局部快照
playwright-cli snapshot --depth=4
playwright-cli snapshot e34

# 在快照中附上每个元素的包围盒 [box=x,y,width,height]
playwright-cli snapshot --boxes

# 在大快照里搜索而不是整页抓取——返回匹配节点
# 及前后各 3 行上下文（类似 grep -C）
playwright-cli find "Add to cart"
playwright-cli find --regex "\\$[0-9]+\\.[0-9]{2}"
```

## 定位元素

默认用快照里的 ref 与页面元素交互。

```bash
# 获取带 ref 的快照
playwright-cli snapshot

# 用 ref 交互
playwright-cli click e15
```

也可以用 CSS 选择器或 Playwright locator。

```bash
# CSS 选择器
playwright-cli click "#main > button.submit"

# role locator
playwright-cli click "getByRole('button', { name: 'Submit' })"

# test id
playwright-cli click "getByTestId('submit-button')"
```

## 浏览器会话

```bash
# 创建名为 mysession 的新浏览器会话，使用持久化配置
playwright-cli -s=mysession open example.com --persistent
# 手动指定配置目录时同理（仅当用户明确要求时用）
playwright-cli -s=mysession open example.com --profile=/path/to/profile
playwright-cli -s=mysession click e6
playwright-cli -s=mysession close  # 关闭命名浏览器
playwright-cli -s=mysession delete-data  # 删除持久化会话的用户数据

playwright-cli list
# 关闭所有浏览器
playwright-cli close-all
# 强制杀掉所有浏览器进程
playwright-cli kill-all
```

## 安装

若全局没有 `playwright-cli` 命令，可试本地版：`npx playwright cli`：

```bash
npx --no-install playwright --version
```

本地可用时，所有命令改用 `npx playwright cli`。否则把 `playwright-cli` 装成全局命令：

```bash
npm install -g @playwright/cli@latest
```

## 示例：表单提交

```bash
playwright-cli open https://example.com/form
playwright-cli snapshot

playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot
playwright-cli close
```

## 示例：多标签页流程

```bash
playwright-cli open https://example.com
playwright-cli tab-new https://example.com/other
playwright-cli tab-list
playwright-cli tab-select 0
playwright-cli snapshot
playwright-cli close
```

## 示例：用 DevTools 调试

```bash
playwright-cli open https://example.com
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli console
playwright-cli requests
playwright-cli close
```

```bash
playwright-cli open https://example.com
playwright-cli tracing-start
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli tracing-stop
playwright-cli close
```

## 示例：交互式会话

请用户做 UI 评审或设计反馈。用户在实况页面上画框并写评论；你会收到带标注截图、标记区域的快照，以及用户备注。用户提到「UI 评审」「设计反馈」，或「问问用户怎么想 / 想要什么 / 是什么意思」时用这个：

```bash
playwright-cli open https://example.com
playwright-cli show --annotate
```

## 专项任务

* **运行与调试 Playwright 测试** [references/playwright-tests.md](references/playwright-tests.md)
* **请求 Mock** [references/request-mocking.md](references/request-mocking.md)
* **运行 Playwright 代码** [references/running-code.md](references/running-code.md)
* **浏览器会话管理** [references/session-management.md](references/session-management.md)
* **存储状态（cookies、localStorage）** [references/storage-state.md](references/storage-state.md)
* **测试生成（plan / generate / heal）** [references/test-generation.md](references/test-generation.md) — 先逐步点完再出测试文件
* **Tracing** [references/tracing.md](references/tracing.md)
* **视频录制** [references/video-recording.md](references/video-recording.md)
* **检查元素属性** [references/element-attributes.md](references/element-attributes.md)
