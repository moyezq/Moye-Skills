# 按需章节

用户点名，或场景已经命中下面某一行时才读、才加依赖。没点名就不装。加了就用本页这一个库，不再选型。

完成标准：本次新装的按需库是下表那一个；脚手架默认依赖列表没有变出表外的包。

## 何时用

**用**：用户说要动画 / 拖拽 / 中英切换 / 登录守卫 / 怎么部署。

**不用**：新建项目的默认路径——见 [scaffold.md](./scaffold.md)。

## 库

| 场景 | 做 |
|------|-----|
| 简单显隐、hover | Tailwind / CSS `transition` |
| 手势、布局动画、页面转场 | `framer-motion` |
| 拖拽排序 | `@dnd-kit/core` + `@dnd-kit/sortable` |
| 中英或多语言 | `react-i18next` |
| 日期计算、格式化 | `date-fns`；能 `Intl` 解决的用 `Intl` |
| 图标 | `lucide-react`（与 shadcn 同一套） |
| 无障碍 | 语义化 HTML、label、键盘；不另装无障碍组件库 |
| Toast | `pnpm dlx shadcn@latest add sonner`，在 mutation 的 `onSuccess` / 页面 `isError` 里调，不在 `http.ts` 里调 |
| 必须渲染 HTML 字符串 | 用户点名才做：`dompurify` 后再 `dangerouslySetInnerHTML` |

```tsx
// ✅ 用户要拖拽排序
import { DndContext } from '@dnd-kit/core'

// ❌ 用户要一点动效就装 react-spring + framer-motion
```

## 认证

脚手架不预装认证 SDK。

- 当前用户放 `stores/session-store.ts`。
- 需要登录的路由在 `loader` 里读会话，没有用户就 `throw redirect('/login')`。
- `http.ts` 遇到 401 清会话；页面用 Query 的 `isError` 或路由 `errorElement` 带到登录。
- 权限码在 loader 或页面里读 `user.roles`，不另装 ACL 库。

```ts
// ✅
export function protectedLoader() {
  const user = useSessionStore.getState().user
  if (!user) throw redirect('/login')
  return null
}

// ❌
pnpm add next-auth
```

## 部署

- 前端包目录执行 `pnpm build`，产物 `dist/`。
- Nginx 或后端静态托管 `dist/`；SPA 回退 `index.html`。
- 不把 Vercel / Netlify 当默认。用户点名再按他们的平台写。

```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```
