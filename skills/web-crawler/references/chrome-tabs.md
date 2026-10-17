# 用户 Chrome：列标签并取当前页

web-crawler 的能力之一。只在 SKILL.md 选路判定要接到**用户本机 Chrome / Edge** 时读（不是 harness 自带标签，不是 CLI 空白会话）。

整场任务只建 **一条** WebSocket。用户至多点一次 Allow。

## 目录

1. [最短路径](#最短路径)
2. [可接入](#可接入)
3. [列标签](#列标签)
4. [取当前页](#取当前页)
5. [脚本](#脚本)

完成标准（整份）：同一条连接上已经拿到 SKILL.md §4 的三样（URL / 标题、登录墙还是业务页、任务字段）；连接只建立过 1 次；用户外部浏览器仍在运行。

---

## 最短路径

1. 读 `DevToolsActivePort` 两行，连 `ws://127.0.0.1:<端口><第2行路径>`。握手不要带 `Origin`。
2. `Target.getTargets`，在 **这一条连接上** 找 `type=page` 且 URL 含目标站的项。
3. `Target.attachToTarget` `{ targetId, flatten: true }`，记下 `sessionId`。
4. 带 `sessionId` 发 `Runtime.evaluate`，取 `location.href`、`document.title`、任务需要的正文或状态对象。
5. `Target.detachFromTarget` 或直接断开进程。不要发 `Browser.close`。

60 秒内任一步走不完：判该接入点超时不可用，不重试。握手超时的默认解释是远程调试弹了 Allow、用户没点到；告诉用户去 `chrome://inspect/#remote-debugging` 点一次，不要怀疑脚本或网络，也不要立刻再连。Allow 没有「授权 N 小时」：勾选开关会留下，每条新 WebSocket 仍要点一次。

```text
✅ 一条连接：握手 → getTargets → attach → evaluate → detach
✅ 整场任务一个 node 进程：握手 → getTargets → attach → 多次 evaluate / 开 Network
❌ 列完标签断开，取正文时再连一次
❌ 每一步一个握手脚本，跑完就断开
❌ `attach --cdp=chrome`、CLI `tab-list`、GET `/json/version`
❌ `Browser.close`
```

---

## 可接入

同时成立才算可接入：

1. 该浏览器用户数据目录下存在 `DevToolsActivePort`：第 1 行端口，第 2 行 WS 路径。
2. 能连上 `ws://127.0.0.1:<端口><WS路径>`。

Windows 默认目录：Chrome 为 `%LOCALAPPDATA%\Google\Chrome\User Data`；Edge 为 `%LOCALAPPDATA%\Microsoft\Edge\User Data`。

```text
✅ 读到两行并握手成功 → 可接入；之后命令都用这条连接
✅ 超时 → 告诉用户去 chrome://inspect/#remote-debugging 点 Allow
❌ 端口在听，但用 GET `/json/version` 或 `/json/list` 的 404 宣布不可接入
❌ 只把第 1 行端口交给「连 http://localhost:<端口>」来判断（会丢掉第 2 行，一直等待）
❌ 握手带 `Origin`（`devtools://devtools` / `http://localhost:9222` / `chrome://inspect` 均为 403）
❌ 路径不对还在等（错误路径上不带 Origin 的升级会静默挂住）
❌ 超时 → 怀疑脚本、代理、防火墙，或自动重连
❌ 握手超时后改 GET `/json/version` 或 `attach --cdp=chrome`
```

开关模式下 Chrome **按每条进来的连接**弹 Allow。点过之后不要断开再连。未弹 Allow 不等于已经用 `--remote-debugging-port` 启动——授权可能仍有效。用户不在场、或不点授权：不要轮询，请用户点这一次。不要中途杀掉半开的握手（会把端点卡住一段时间）。

---

## 列标签

用 `Target.getTargets` 的 `targetInfos`。只要 `type=page` 的项；`service_worker`、DevTools 窗口不要当成业务标签。

每条记四态之一（与 SKILL.md §2 相同）：未开目标站 / 开着但是登录墙 / 开着且有业务数据 / 超时不可用。

目标站有多条 page 时，选 URL 最贴近用户要的那条（路径、query），不要随便拿第一条。

```text
✅ getTargets 里该页有正常 URL，再 attach
❌ 用会先读每个 `page.url()` 的 CLI `tab-list`（目标页 `page.url()` 可能恒为空串，命令一直等）
```

---

## 取当前页

`Runtime.evaluate` 带 `returnByValue: true`。先取 href / title / `document.readyState`，再取任务字段。

页面里的状态对象若含 JS 字面量 `undefined`，先换成 `null` 再当 JSON 解析。不要用把不同大小写键当成冲突的解码器去吃这份对象。

取完 `detach` 或断开。用户浏览器继续运行。

```text
✅ evaluate 返回 href / title / 正文，然后断开
❌ 接入后 `page.url()` 空串就空等；改走本页「最短路径」第 2–4 步
❌ 滚动、点击、代填登录
```

---

## 脚本

要实际握手并取页时跑本 skill 的 `scripts/chrome-tabs.mjs`（Node 22+ 自带 `WebSocket`），参数是 URL 子串：

```text
node "<本 skill>/scripts/chrome-tabs.mjs" "example.com/path"
```

可选环境变量 `CHROME_USER_DATA_DIR` 覆盖用户数据目录。标准输出一份 JSON：连接、target 列表、选中的页、`href` / `title` / `readyState` / `bodyText`。超时 60 秒。不发 `Browser.close`。
