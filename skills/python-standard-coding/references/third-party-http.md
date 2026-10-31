# 第三方 HTTP 客户端

命中「封装调第三方 HTTP 的模块、按真实返回写分支」时读本文。探测脚本形态见 [script.md](./script.md)「一次请求」。密钥和地址放哪见 [project.md](./project.md)。

完成标准：客户端只覆盖已经打到的返回；业务层不组 HTTP。

## 一个模块对外

被两个以上业务模块调用的第三方 HTTP，单独成一个类。业务层只调这个类、只看它分好类的返回。

✅ 入库 enrich 和在线 generate 都调 `ChatClient.complete()`，看 `reply.kind`  
❌ `enrich.py` 和 `generate.py` 各自 `requests.post`，各自解析 `choices[0]`

密钥、地址、模型名只 `os.getenv`。空就是未配置。类里、模块级都不要再备一份默认 URL 或默认模型。项目已有读 `.env` 的入口时，客户端不再自己读文件。

## 先打再写

写客户端之前，每种会打到的返回用一份一次请求脚本打真实接口，打印 status 和 body。客户端只为这些 body 写分支。

官方文档列出、这次请求打不到的字段和状态，不预留。客户端不发送的能力（流式、工具、思考链），不为它们的返回写分支。

✅ 探测打到 `200` + `finish_reason=stop|length`，非 200 时 `body["error"]["message"]` → 客户端只分这几类  
❌ 按文档把 `tool_calls`、`content_filter`、空 content、`reasoning_content` 全写成 if

嵌套字段按打到的形状直取。`json.loads` 只包会真抛 `JSONDecodeError` 的那一次。

✅ `choice = body["choices"][0]`; `content = choice["message"]["content"]`  
❌ `if isinstance(body, dict) and body.get("choices"):` … 再对 `message` 做一层 `get`

配置空了就返回未配置，不要用另一套默认值顶上。

✅ `key = os.getenv("CHAT_API_KEY")`；空 → `kind=not_configured`  
❌ `key = os.getenv("CHAT_API_KEY") or "https://api.example.com/v1"` 或类属性 `DEFAULT_URL`
