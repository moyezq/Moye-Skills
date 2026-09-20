# 静态构建站 1:1 镜像

适用：Astro / Vite SSG / Hugo / Eleventy 等把客户端打成可下载静态资产的站，哪怕重 WebGL。不适用：真 SSR / 数据在 API 后的 SPA → `network-capture.mjs`。

对这类站，「拿到真源码」= 镜像部署资产整套（HTML + bundle + 运行时 fetch 的 `.sog/.buf/.wasm/.riv` / 字体）。`astro:true` 且是定制站 → 走镜像，不走主题市场。

二进制常按滚动进度动态 fetch，`wget --mirror` 抓不全。用真浏览器滚完全页记请求再镜像：

```
node $S\mirror-site.mjs --url <原站> --out $R
```

产物：`$R\site\` 同源资产、`own-asset-urls.txt`、`third-party.json`、`mirror-manifest.json`。

手工收尾（脚本不改写第三方）：

1. 锁域名 webfont（常见 Typekit）：下 kit CSS 与 `@font-face` 字体到 `site/typekit/`，改成本地 `@import`。同一字体常有 woff2/woff/otf，以文件魔数为准。
2. 精确删追踪 script。
3. 公共 CDN player 可留在线（离线失效，NOTES 标注）。Vimeo/YouTube iframe 同理。

从 `site/` 作 web 根：`python -m http.server 8124`。重 WebGL 要滚到各段再截图对照。
