# 路由与页面壳

命中「加页面、嵌套布局、懒加载、URL 参数、筛选进地址栏、404、登录守卫」时读本文。守卫细节与部署见 [ondemand.md](./ondemand.md)。数据请求见 [data.md](./data.md)。

完成标准：新页面挂在 `createBrowserRouter` 的 `children` 里；共享壳用 `Outlet`；非首页路由 `lazy`；筛选读写 `useSearchParams`。

## 何时用

**用**：加路由、拆 layout、读 `:id`、读 `?status=`、做 404、做需登录页。

**不用**：只改某个卡片组件。只改 Query。

## 配置

只用对象形 `createBrowserRouter`（教程里「大型应用」那条，也是本栈锁死的库模式）。JSX `<Routes>` / `<BrowserRouter>` 不写。

根上一个壳：顶栏 / 侧栏放壳里，内容区 `<Outlet />`。认证页可以另做一套壳。收尾一条 `path: '*'`。

```tsx
// ✅
export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <RouterErrorElement />,
    children: [
      { index: true, element: <HomePage /> },
      {
        path: 'orders',
        element: <OrdersLayout />,
        children: [
          { index: true, Component: LazyOrderListPage },
          { path: ':orderId', Component: LazyOrderDetailPage, loader: orderLoader },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])

export function AppLayout() {
  return (
    <div className="flex min-h-svh">
      <aside />
      <Outlet />
    </div>
  )
}

// ❌
<BrowserRouter>
  <Routes>
    <Route path="/orders" element={<OrderListPage />} />
  </Routes>
</BrowserRouter>
```

非首页、非壳：`lazy(() => import('@/routes/OrderListPage').then((m) => ({ default: m.OrderListPage })))`。`lazy` 要 default，本栈组件是具名导出，所以 `.then` 这一下是固定写法。壳和 `AppProviders` 同步 import。`Suspense` 只包懒加载出口（R8），不要给 Query 开 suspense。

## 参数

路径参数 `useParams()`，值是字符串。查询参数 `useSearchParams()`，列表筛选只写这里，不另起一份 `useState` 当页码源。

```tsx
// ✅
const { orderId } = useParams()
const [params, setParams] = useSearchParams()
const status = params.get('status') ?? 'all'
const page = Number(params.get('page') ?? '1')
function onStatus(next: string) {
  const nextParams = new URLSearchParams(params)
  nextParams.set('status', next)
  nextParams.set('page', '1')
  setParams(nextParams)
}

// ❌
const [status, setStatus] = useState('all')
const [page, setPage] = useState(1)
useEffect(() => { fetchOrder(orderId).then(setOrder) }, [orderId])
```

内部跳转用 `<Link to>` / `useNavigate`。带查询：`to={{ pathname: '/orders', search: nextParams.toString() }}`。

## 需登录的路由

`loader` 里读会话，没有用户就 `throw redirect('/login')`。登录成功回到 `location.state.from`，没有则 `/`。不要在每个页面里自己 `if (!user) return <Navigate />` 复制一份（教程基础守卫可以，但本栈路由已锁 loader）。

```ts
// ✅
export function protectedLoader({ request }: LoaderFunctionArgs) {
  const user = useSessionStore.getState().user
  if (!user) {
    const url = new URL(request.url)
    const from = `${url.pathname}${url.search}`
    throw redirect(`/login?from=${encodeURIComponent(from)}`)
  }
  return null
}

// ❌
if (!user) window.location.href = '/login'
```
