---
name: react-standard-coding
description: >-
  React + Vite + TypeScript 的写法与落盘：脚手架、目录、函数组件与 Hooks、
  React Router、Zustand、TanStack Query、Tailwind、shadcn/ui、表单、Vitest。
  写或改 .tsx / .ts / .css 前端、新建 Vite React 项目、加页面 / 组件 / 路由 / 表单 / 请求、
  整理 src 或 frontend/ 目录时查阅。
  不管 Next.js、Remix、Astro、React Native、仿站、类组件、PropTypes、面试题。
---

# React 写法与落盘

管 **Vite SPA 怎么建、React 怎么写、文件放哪、请求与状态怎么分、表单与样式用哪一套**。

## 何时用

**用**：写或改 `.tsx` / `.ts` / `.css` 前端；新建 Vite React 项目；加页面、组件、路由、表单、请求；整理 `src/` 或 `frontend/`；给已有仓加符合本栈的新文件。

**不用**：Next.js / Remix / Astro / RSC；React Native / PWA；整站复刻；类组件与 PropTypes；面试题与手写 React 内部；只改后端 Python / 项目文档、不动前端文件。

## 锁死技术栈

| 层 | 只用 |
|---|---|
| 包管理 | pnpm |
| 应用 | React 19 客户端 + Vite + TypeScript `strict` |
| 路由 | React Router v7 库模式：`createBrowserRouter` + `RouterProvider` |
| 客户端状态 | Zustand。Context 只给主题 / 语言。仓库里已有 Redux 才跟 Redux |
| 服务端状态 | TanStack Query + `src/lib/http.ts` 包过的 `fetch` |
| 样式 / UI | Tailwind CSS v4 + shadcn/ui + lucide |
| 表单 | React Hook Form + Zod |
| 测试 / 风格 | Vitest + RTL；ESLint flat + Prettier |
| 错误边界 | `react-error-boundary`（根上挂） |

完成标准：新文件与本次改动的文件只出现上表里的库；表外的库用户没点名就不装。

## 技能清单

| 任务 | 读 |
|------|-----|
| 新建 Vite React 项目、第一次搭本栈 | [references/scaffold.md](./references/scaffold.md) |
| 目录树、`@` 别名、`VITE_` 环境变量、同仓 `frontend/` | [references/project.md](./references/project.md) |
| 组件、Hooks、TS、导出与文件名、表单 | [references/write.md](./references/write.md) |
| `http.ts`、Query 键工厂、Zustand | [references/data.md](./references/data.md) |
| 嵌套路由、Outlet、懒加载、search params | [references/routes.md](./references/routes.md) |
| Vitest、RTL、ESLint、Prettier | [references/quality.md](./references/quality.md) |
| 动画、拖拽、i18n、认证守卫、静态部署 | [references/ondemand.md](./references/ondemand.md) |

完成标准：命中「按任务读哪一块」的每一块，该块要求都做到。带「何时读」的 reference 只在条件满足时读。

---

## 全局规则

### R1 TypeScript：`strict`，不用 `any`

对象形状用 `interface`，联合用 `type`。细则见 [write.md](./references/write.md)。

```ts
// ✅
function parseId(raw: unknown): string {
  if (typeof raw !== 'string') throw new Error('invalid id')
  return raw
}

// ❌
function parseId(raw: any): string {
  return raw
}
```

### R2 一个文件一个组件；文件名 PascalCase；具名导出

```tsx
// ✅ 文件：UserCard.tsx
export function UserCard({ name }: { name: string }) {
  return <article>{name}</article>
}

// ❌
export default function UserCard() { return null }
export function UserCardSkeleton() { return null }
```

shadcn 生成的 `components/ui/*` 保持原样，不按这条拆。

### R3 不用 `useEffect` 拉数据，也不用它同步两份 state

```tsx
// ✅
const { data } = useQuery({ queryKey: userQueryKey(id), queryFn: () => fetchUser(id) })
const fullName = `${user.firstName} ${user.lastName}`

// ❌
useEffect(() => { fetchUser(id).then(setUser) }, [id])
useEffect(() => { setFullName(`${user.firstName} ${user.lastName}`) }, [user])
```

### R4 动态列表的 `key` 用稳定 id

```tsx
// ✅
{users.map((user) => <UserCard key={user.id} name={user.name} />)}

// ❌
{users.map((user, index) => <UserCard key={index} name={user.name} />)}
```

### R5 条件渲染用布尔值；提前 return

```tsx
// ✅
if (!count) return null
return <Badge>{count}</Badge>

// ❌
{count && <Badge>{count}</Badge>}
```

### R6 Zustand 按字段订阅；服务端列表不进 store

```ts
// ✅
const name = useSessionStore((s) => s.user?.name)
const { data: users } = useQuery({ queryKey: ['users'], queryFn: fetchUsers })

// ❌
const snap = useSessionStore()
const users = useSessionStore((s) => s.users)
```

### R7 `queryKey` 用数组工厂；mutation 成功后 `invalidate`

```ts
// ✅
export const userQueryKey = (id: string) => ['users', id] as const
onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ['users'] }) }

// ❌
useQuery({ queryKey: 'user-' + id, queryFn })
```

### R8 根上挂 `ErrorBoundary`；数据加载用 Query 的 `isPending` / `isError`

路由懒加载才用 `Suspense`。Query 不开 suspense 模式。

### R9 同仓把 `/api` 代理到后端；环境变量只以 `VITE_` 开头

### R10 不改 `components/ui` 里 shadcn 生成的代码；要改就在外面包一层

### R11 只约束新文件和本次改动的文件；不主动换旧依赖、不整仓迁移

### R12 不开 React Compiler

完成标准：本次改动的每个 `.ts` / `.tsx` 都过 R1–R12。
