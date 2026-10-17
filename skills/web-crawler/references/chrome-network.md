# 用户 Chrome：同一条连接拦请求

只在已经按 chrome-tabs 接到目标页之后读。禁止为这一步再建立 WebSocket。

## 最短路径

1. 在已有 sessionId 上发 `Network.enable`。
2. 等 `Network.requestWillBeSent`（url + POST body）和 `requestWillBeSentExtraInfo`（大小写不统一的头、有时才出现的 Cookie）。
3. 请求头里没有 Cookie 时，同连接发 `Network.getCookies`，不要改判「没登录」。
4. 落到磁盘后 `Network.disable` 或断开。不发 `Browser.close`。

60 秒内没有匹配请求：先问用户是不是还开着 XHR / `debugger` 断点把页面卡死了。不要重连。默认等人在页面里触发该请求，不要脚本自己 `reload` / `scroll`。

```text
✅ 一条已有连接上 enable → 事件 → getCookies → 落盘
❌ 为了采这一条再 new WebSocket
❌ 只看 request headers、没有 ExtraInfo / getCookies 就宣布缺 Cookie
❌ 让人在 Sources 作用域树里抄即将发出的头
❌ 每个 analyse 步骤一份握手脚本
```

落到可跑 `.py` 时：headers → cookies → body → `url` 紧挨着 `requests.get` / `requests.post` → 解析 → 落盘。不封装、不用 `main`。

完成标准：磁盘上有一条完整请求（方法、URL、body、自定义头、Cookie）；本步没有新建连接。
