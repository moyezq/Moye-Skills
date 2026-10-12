# 症状 → 处置

`self-react` 的披露参考：只在遇到下面这些症状时读。命令示例是 Windows + PowerShell；换平台时换成等价写法。

## dev server 像在提供旧代码

**症状**：源文件已经改了，页面行为还是旧的；更明显的是错误信息指向**源码里已经不存在的变量**。

**先确认服务端到底给的是新版还是旧版**，比反复刷新页面有用得多——直接取模块源码看一眼（下面的端口是 Vite 默认的 dev 端口，按实际改）：

```powershell
$src = (Invoke-WebRequest 'http://localhost:5173/src/App.tsx' -UseBasicParsing).Content
if ($src -match '新代码里的标志性字符串') { '服务端已是新版' } else { '服务端仍是旧版' }
```

**原因**：dev server 的模块转换缓存没失效。Windows 上文件常以「写临时文件再改名」的原子方式替换，文件监听可能漏掉事件。

**处置顺序**（从轻到重，别一上来就改代码）：

1. **只更新 mtime** 触发重新编译：

   ```powershell
   (Get-Item src\App.tsx).LastWriteTime = Get-Date
   ```

2. 仍不行再重启 dev server，并清掉转换缓存目录（Vite 是 `node_modules/.vite`）。

3. 在浏览器里**硬刷新**（Ctrl+Shift+R）。

改完源文件后要提醒使用者硬刷新，不要把正在跑的旧页面当成新代码已通过。

## 编辑后页面崩了，或状态被莫名清空

React Fast Refresh 会**重置被编辑组件自身的状态**。编辑持有 state 的组件之后，要重新走一遍流程再验收，不能拿着「刚才那次的结果」判断新代码。

若错误指向一个源码里已不存在的变量，先怀疑上面那条「服务端仍是旧版」，而不是新代码。

## 依赖装上了但行为不对

较新的 npm 默认拦截 install script（典型是 esbuild 的 postinstall）。**先确认平台二进制是否真的在位**，再判断要不要放行：

```powershell
Get-ChildItem node_modules -Recurse -Filter esbuild.exe -ErrorAction SilentlyContinue | Select-Object -First 1
```

在位就说明拦截没有造成实际影响，不必为此改动安装策略。

## 类型错指向生成物（`Cannot find module`、命名空间缺成员）

**症状**：类型检查报「找不到某个模块」，或「某个命名空间没有导出某个成员」，而那个文件**确实在盘上、也确实在编译范围里**（`--listFiles` 能看到它）。此时改 `tsconfig` 的解析、路径、include/exclude 全是白做功。

**先验生成物本身**，它对不对是另一件事：

- 声明的成员在生成文件里真的存在吗——框架生成的 `.d.ts` 常声明了实现文件里其实没有的命名空间。一条 `Select-String` 就够：

  ```powershell
  # 声明里列的每个导出，在生成文件里都应当能找到
  Select-String -Path path\to\bindings\*.d.ts -Pattern '^export function (\w+)' |
    ForEach-Object { $n = $_.Matches[0].Groups[1].Value
      if (-not (Select-String -Path path\to\generated.ts -Pattern "function $n\b" -Quiet)) { "缺: $n" } }
  ```

- 生成物是**这一版**的吗：源码里新加的方法/字段在生成文件里有没有。框架的生成物过期时，症状正是上面这类模块解析错。
- 过期就重跑那条生成命令，**不要改产物**；有些框架没有单独的「只生成」命令，生成与构建是同一个入口（Wails 就是 `wails build`）。

## 沙箱或受限环境里装依赖失败

**只有缓存目录被拒时**，把缓存指到工作区内即可（用完删掉，别入库）：

```powershell
npm install --cache .\.npm-cache
```

**构建命令本身被拒**（编译器或包管理器写自己的缓存/临时目录时报 `Access is denied`、`EPERM`）就不一样了：**换目录、换临时目录都绕不过去**，那是环境的硬边界。对**那一条命令**提权一次，别在受限模式里变着法子重试。

会话级的沙箱边界与提权规矩，见 `session-bootstrap/` 下当轮 harness 那一份（`agent-dsh.md` / `agent-cursor.md` / `agent-codex.md`）的「权限与提权」一节。

## 剪贴板与权限类 API 静默失败

`navigator.clipboard`、地理位置、通知等只在**安全上下文**可用——`localhost` 算安全上下文，局域网 IP 不算。

这类调用一律 **fail soft**：写在 `try/catch` 里，失败也不中断主流程。主流程（例如把值填进输入框）该照常完成，复制只是附带动作。

## 前后端联调的两个无效配置

- **通配来源 + 携带凭证是无效组合**，浏览器会拒绝。服务端应当设 `allow_credentials: false`；真要带凭证就必须写出具体来源，不能用 `*`。
- **错误响应上没有 CORS 头**：自己写的中间件若要在错误响应（如体积超限、鉴权失败）上带跨域头，**CORS 中间件必须在最外层**——即最后注册。否则浏览器里看到的是一个 CORS 报错，而不是你精心写的错误消息。

## 请求全部失败且看不出原因

先查**代理目标端口**是否与后端实际端口一致。dev proxy 的目标通常是写死在配置里的一个值，后端换了端口而代理没跟着改，症状就是前端全挂、控制台只有网络错误。

在配置文件里对这条耦合写一句注释，是成本最低的预防。
