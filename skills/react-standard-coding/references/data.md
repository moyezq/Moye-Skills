# 请求、Query、Zustand

命中「写请求、缓存、全局客户端状态、401」时读本文。全局 R3、R6、R7、R9 仍生效。

完成标准：服务端数据只从 Query 读；`fetch` 只出现在 `src/lib/http.ts`；每个资源有一份 queryKey 工厂；组件里用 `useXxx` 包装，不裸写 `useQuery` 散落各处。

## 何时用

**用**：加 API 调用、列表 / 详情缓存、登录态、mutation、筛选分页。

**不用**：本地 UI 开关、输入框。表单字段见 [write.md](./write.md)。筛选进 URL 见 [routes.md](./routes.md)。

## 分界

| 数据 | 放哪 |
|------|------|
| 服务端资源（列表、详情、配置接口） | TanStack Query |
| 跨页客户端会话（当前用户） | Zustand，按领域一个文件 |
| 主题 / 语言 | Context 或 i18n 库，不进 Zustand |
| 一个组件内部的开合、hover | `useState` |
| 列表筛选、页码 | URL search params，再进 queryKey |

```ts
// ✅
const { data } = useOrders({ status, page })

// ❌
const orders = useOrderStore((s) => s.orders)
useEffect(() => { fetch('/api/orders').then((r) => r.json()).then(setOrders) }, [])
const [page, setPage] = useState(1)
```

## http.ts

- 拼接 `VITE_API_BASE`、JSON、`credentials: 'include'`。
- 响应当 `unknown` 再交给调用方的 Zod / 泛型，不要 `any`。
- 非 2xx throw `HttpError`；`401` 先 `useSessionStore.getState().clearUser()` 再 throw。
- 不在这里 toast、不在这里 `navigate`。

```ts
// ✅
export async function fetchOrder(id: string): Promise<Order> {
  return http<Order>(`/api/orders/${id}`)
}

// ❌
export async function fetchOrder(id: string) {
  const r = await fetch('http://localhost:8000/api/orders/' + id)
  return r.json()
}
```

## Query

每个 feature 三件套：`api.ts`（只调 `http`）→ `xxx-keys.ts`（键工厂）→ `use-xxx.ts`（`useQuery` / `useMutation`）。页面只调 Hook。

```ts
// ✅ features/orders/order-keys.ts
export const orderKeys = {
  all: ['orders'] as const,
  lists: () => [...orderKeys.all, 'list'] as const,
  list: (filters: { status: string; page: number }) => [...orderKeys.lists(), filters] as const,
  details: () => [...orderKeys.all, 'detail'] as const,
  detail: (id: string) => [...orderKeys.details(), id] as const,
}

// ✅ features/orders/use-orders.ts
export function useOrders(filters: { status: string; page: number }) {
  return useQuery({
    queryKey: orderKeys.list(filters),
    queryFn: () => fetchOrders(filters),
  })
}
export function useOrder(id: string) {
  return useQuery({
    queryKey: orderKeys.detail(id),
    queryFn: () => fetchOrder(id),
    enabled: id.length > 0,
  })
}
export function useCreateOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createOrder,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: orderKeys.lists() })
    },
  })
}

// ❌
useQuery({ queryKey: 'orders-' + page, queryFn: () => fetch('/api/orders').then((r) => r.json()) })
```

- 默认 `staleTime: 5 * 60 * 1000`、`retry: 1`（写在 `query-client.ts`）。
- 缺 id / 缺前置数据：`enabled: false` 或 `enabled: id.length > 0`。后一个查询依赖前一个数据时，用前一个的字段做 `enabled`。
- 页面分支：`isPending` / `isError` / `data`。空列表 `data.length === 0`，与 error 分开。
- 分页切换不断空白：`placeholderData: keepPreviousData`（`import { keepPreviousData } from '@tanstack/react-query'`）。
- 乐观更新只在用户点名时写。

## Zustand

- `create` + 按字段选择器。不要 `const s = useXxxStore()` 订阅整棵。
- 选出对象时用 `useShallow`，避免每次新引用。
- 更新用 `set((state) => ({ count: state.count + 1 }))`，不要先 `get()` 再拼一份可变原对象。
- `persist` 只给刷新后仍要在的会话字段。列表、详情禁止 persist。
- 真要中间件：外 → 内 `devtools → persist → immer`。默认脚手架不装 immer / devtools。
- 已有 Redux 的文件继续用 Redux；新文件仍用 Zustand。

```ts
// ✅
import { useShallow } from 'zustand/react/shallow'
const name = useSessionStore((s) => s.user?.name)
const { width, height } = useUiStore(useShallow((s) => ({ width: s.width, height: s.height })))
increment: () => set((state) => ({ count: state.count + 1 }))

// ❌
const snap = useSessionStore()
const size = useUiStore((s) => ({ width: s.width, height: s.height }))
increment: () => set({ count: get().count + 1 })
```
