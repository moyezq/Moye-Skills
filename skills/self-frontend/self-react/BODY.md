---
name: self-react
description: React 页面 / 布局 / 界面验收（Vite + TypeScript）。加页面、改布局、调滚动、前后端联调、镜像类型、界面验收时查阅；dev server 像在提供旧代码时也查阅。界面验收用几何测量。通用原则见 self-code-principles；点选与快照见 playwright-cli。
---

# React 页面 / 布局 / 界面验收

管 **页面怎么写、布局怎么定、界面怎么验收**。默认 Vite + TypeScript；换构建工具时只换命令，规范本身不变。

12 条判断见 `self-code-principles`（冲突点以本文件为准，不是整份跳过那份）。目录分层见 `self-python-project`。点选、结构快照见 `playwright-cli`。

完成标准：类型与构建门禁都 exit 0；写了 `.ts` / `.tsx` 则 `references/typescript.md` 的完成标准都做到；改布局则五个几何断言都给出数字；每个改动过的交互都真点过。逐条都做到才算完成。

## 何时用

**用**：写或改 React 组件、页面、样式；调布局 / 高度 / 滚动；改前后端联调或镜像类型；验收界面；dev server 像在提供旧代码。

**不用**：只改一处颜色或字号；非 React 前端；后端接口实现。

写或改 `.ts` / `.tsx`、镜像类型、API 模块类型：读 `references/typescript.md`。
源文件改了页面仍是旧的、HMR 后错误指向已删变量、依赖装上但行为不对：读 `references/troubleshooting.md`。

---

## 门禁

| 门禁 | 命令 | 它挡什么 |
|------|------|----------|
| 类型 | `npx tsc --noEmit` | 类型错误、未使用的变量与参数 |
| 构建 | `npx vite build` | 模块解析、CSS、打包期错误 |
| 功能 | 浏览器里真点一遍 | 交互是否真通（见「验收」） |

`vite dev` **不做类型检查**。改完先过类型与构建，再去浏览器点。这两条是本 skill 的检查点，不是会话索引禁止的业务脚本。

tsconfig 要求见 `references/typescript.md`。依赖选稳定线（当前大版本），lockfile 入库。

用户说构建慢或产物异常大时，先 `npx vite-bundle-visualizer`，看清大包再改分包或依赖。

## API 调用

组件不直接 `fetch`。请求体成形、响应解析、错误包装放在一个 API 模块里，组件只调函数。彼此独立的请求在 API 模块里一并发出；有先后依赖的保持链式。

开发期走 dev proxy + 相对路径（`/api/...`），不把后端地址硬编码进构建产物。代理目标端口与后端端口写在配置注释里点明耦合。

## 组件职责

- **容器组件**持有状态、数据流与副作用；**展示组件**只接 props 渲染，不自己取数据。
- **动作与 loading 归属到它作用的区域**：每个区域自己的按钮与 loading，耗时与结果互不干扰。
- **派生状态**渲染时计算，不用 `useEffect` 去 `setState`。
- **订阅 / timer / 动画**的 effect 在 `return` 里清掉。
- **动态列表**的 `key` 用稳定 id，不用 `index`。

## 布局：固定区域 + 单滚动条

目标：区域按屏幕分配高度、底色铺满，整页不滚动，**只有真的超出时才出滚动条**。

配方（缺一条就塌）：

```css
html, body, #root { height: 100%; }

.layout {
  height: 100%;
  display: grid;
  /* minmax(0, 1fr) 防止长内容（<pre>、长 URL）把栅格撑破 */
  grid-template-columns: minmax(280px, 320px) minmax(0, 1fr) minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}

.region {
  height: 100%;          /* 底色铺满自己的格子，不被内容撑开 */
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.region-body {
  flex: 1;
  min-height: 0;         /* 必需：flex 子项默认不收缩，缺了滚动条永远不出现 */
  overflow-y: auto;      /* 一个区域一根滚动条，就放这里 */
}

.block { flex: none; }   /* 子块按内容自然高度排布 */
```

三条最容易踩反的：

- **一个区域一根滚动条**。给每个子块各自加 `overflow: auto`，会让「统计」「元信息」这类固定块先吃光高度，留给长文本的只剩几十像素。
- **只有真的装得下内容的块才 `flex: 1`**。空状态不占位；没有内容可展示的块按自然高度收起来。
- **窄屏回退**：宽屏才固定区域；窄屏改成堆叠（`grid-template-columns: 1fr`，外层高度改 `auto`），每个区域仍固定高度（如 `72vh`）、内部照旧滚动。

## 内容排布

- 值可能很长并且不能断的行（URL、路径、token、ID）**独占整行**，配 `word-break: break-all`。
- 网格单元保持窄而齐：`grid-template-columns: repeat(auto-fill, minmax(150px, 1fr))`。
- 结构性恒为空或恒为 0 的字段不渲染。
- 空值给空串再渲染，别让 `String(null)` 把 `"null"` 写进界面。
- 界面写使用者认得的说法，不用内部代号（`typ_b`、`mode2`）。

## 命名与样式卫生

- **类名避开布局原语**。内容区块用了 `.block`，就不要再拿 `.block` 当按钮的「全宽」修饰。修饰类用自解释的名字（`.full-width`）。
- **CSS 变量双向查**：没有悬空的 `var(--x)`，也没有定义了没人用的变量。
- **类名双向查**：样式里定义的类都还有人用，组件里用到的类都有定义。

## 验收前

打开浏览器前先看本机已有 dev 端口：只有一个就用它，多个问用户，没有再按项目脚本起。自己起的 dev server 测完立刻停，不要常驻。

## 验收：用测量

界面落到可核查的证据。几何测量的取舍见 `<工作目录>\skills-docs\adr\0009-react-geometry-not-eyeball.md`。

1. **门禁**：`npx tsc --noEmit` 与 `npx vite build` 都 exit 0。
2. **几何测量**——问 DOM：

   | 断言 | 怎么量 |
   |------|--------|
   | 整页不滚动 | `document.documentElement.scrollWidth/scrollHeight` 对比 `innerWidth/innerHeight` |
   | 区域铺满 | 每个区域 `getBoundingClientRect()` 的宽高 |
   | 恰好一根滚动条 | 区域内 `scrollHeight` 与 `clientHeight` 对比（差值 >1 才算溢出） |
   | 零横向溢出 | 遍历容器，找 `scrollWidth > clientWidth + 1` 的元素 |
   | 长值没把行顶高 | 逐个网格单元、以及长值所在行的 `getBoundingClientRect().height` |

   网格单元高度是个被低估的探针：它从 20px 变成 82px，就说明有长值塞进了不该塞的地方。

3. **交互真点一遍**：点按钮 → 检查输入被正确填入 → 检查**只有目标区域**发生变化。走 `playwright-cli` 时用 snapshot / eval，不要只截图。
4. **结构读一遍**：可访问性快照是纯文本，逐字核对层级与文案。
5. **契约一致性**：改了类型则按 `references/typescript.md` 逐字段比对。

没有视觉能力时明说「我看不了截图」，用上面的测量与快照代替。不要凭「渲染出来了」宣布完成。
