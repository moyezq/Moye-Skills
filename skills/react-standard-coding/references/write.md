# 组件、Hooks、TypeScript

命中「写或改组件、Hooks、TS 类型、导出与文件名、表单 UI」时读本文。全局 R1–R5、R8、R10、R12 仍生效。请求见 [data.md](./data.md)。路由见 [routes.md](./routes.md)。

完成标准：本次改动的组件都是函数组件、具名导出、对象 Props 用 `interface`；表单走 React Hook Form + Zod；`useEffect` 不拉数据、有副作用就有清理。

## 何时用

**用**：新建或改 `.tsx` 组件；抽子组件；写 Props / Hooks 类型；写表单；处理定时器 / 订阅。

**不用**：只改 `http.ts` 或 store。只改 CSS class。目录该放哪见 [project.md](./project.md)。

## 命名

| 东西 | 写法 |
|------|------|
| 组件文件 | `UserCard.tsx` PascalCase，不加 `Component` 后缀 |
| 路由页面 | `LoginPage.tsx` |
| 布局 | `AppLayout.tsx` |
| Hook 文件 | `useDebounce.ts`，`use` + camelCase |
| 普通函数文件 | `formatDate.ts` camelCase |
| 常量文件 | `api-endpoints.ts` 或文件内 `API_BASE` |

```tsx
// ✅
export function UserCard() { return null }
export function useDebounce(value: string, ms: number) { return value }

// ❌
export default function user-card() { return null }
export function UseAuth() { return null }
```

## TypeScript

能推断就不写注解。对象形状用 `interface`，联合 / 元组用 `type`。禁止 `any`。

```ts
// ✅
interface UserCardProps {
  user: User
  onEdit: (id: string) => void
  showActions?: boolean
}
type Status = 'idle' | 'loading' | 'success' | 'error'
const [count, setCount] = useState(0)
const [user, setUser] = useState<User | null>(null)

// ❌
type UserCardProps = { user: any }
const [count, setCount] = useState<number>(0)
```

`children` 标 `React.ReactNode`。可选回调写成 `onEdit?: (id: string) => void`，不要 `Function`。

## 组件

一个组件一件事。页面只拼区块；拉数、提交放该区块自己的 Hook（Query / mutation）。变体用配置表或 Props，不要越加越长的 `if (type === ...)`。

```tsx
// ✅
export function UserDashboard() {
  return (
    <>
      <UserProfileSection />
      <UserPostList />
    </>
  )
}

// ❌
export function UserDashboard() {
  const [user, setUser] = useState(null)
  const [posts, setPosts] = useState([])
  useEffect(() => {
    fetchUser().then(setUser)
    fetchPosts().then(setPosts)
  }, [])
  return <div>{user?.name}{posts.length}</div>
}
```

跨 feature 的 UI 放 `components/`，先包 shadcn 再加业务。按钮：提交用 `type="submit"`，其余 `type="button"`。输入必须有可见 `<label htmlFor>`。内部跳转用 `Link`，外链 `rel="noopener noreferrer"`。

```tsx
// ✅
<label htmlFor="email">邮箱</label>
<input id="email" type="email" {...register('email')} />
<button type="button" onClick={onCancel}>取消</button>
<Link to="/orders">订单</Link>

// ❌
<input placeholder="邮箱" {...register('email')} />
<button onClick={onCancel}>取消</button>
<a href="/orders">订单</a>
```

用户可见文本写进 JSX 文本节点。不要 `dangerouslySetInnerHTML`，不要 `eval`。`href` 只允许 `http:` / `https:`。

## Hooks

`useState`：贵的初始值用函数；依赖上一次值用函数式更新；不相干的字段拆开。表单字段不进 `useState`，进 RHF。

```tsx
// ✅
const [count, setCount] = useState(0)
setCount((c) => c + 1)
const [open, setOpen] = useState(false)
const [items, setItems] = useState(() => readCache())

// ❌
setCount(count + 1)
setCount(count + 1)
const [state, setState] = useState({ user: null, loading: false, modalOpen: false })
useState(JSON.parse(localStorage.getItem('x') ?? '[]'))
```

`useEffect`：依赖写全；定时器 / `addEventListener` / 订阅必须 `return` 清理。拉数走 Query（R3）。对象字面量不要当依赖。

```tsx
// ✅
useEffect(() => {
  const id = window.setInterval(() => setTick((t) => t + 1), 1000)
  return () => window.clearInterval(id)
}, [])

// ❌
useEffect(() => {
  fetchUser(userId).then(setUser)
}, [])
useEffect(() => {
  const id = window.setInterval(() => console.log(count), 1000)
  return () => window.clearInterval(id)
}, [])
```

定时器 / 异步回调里要用最新 state：函数式 `setX((x) => ...)`，不要闭包抓渲染当时的值。

`useMemo` / `useCallback` 只给昂贵计算，或已经 `memo` 的子组件且 props 不稳。`count * 2` 这种直接算。

自定义 Hook 一件事、一个文件、只导出它。返回对象。不要做一个 `useUserManager` 里塞用户 / 帖子 / 评论。

```ts
// ✅
export function useToggle(initial = false) {
  const [on, setOn] = useState(initial)
  return { on, toggle: () => setOn((v) => !v) }
}

// ❌
export function useUserManager(id: string) {
  useEffect(() => { fetch(`/api/users/${id}`).then(...) }, [id])
  useEffect(() => { fetch(`/api/users/${id}/posts`).then(...) }, [id])
}
```

## 表单

`useForm` + `zodResolver`。校验 schema 与类型同一份 Zod。`mode` 用 `'onSubmit'`（RHF 默认，也是教程性能节的默认）。`defaultValues` 必须写。

原生控件 `register`；shadcn 控件 `Controller`。错误文案用 `formState.errors.字段.message`。提交只调 mutation / `http`；4xx 校验用 `setError`，不要只 `console.error`。

```tsx
// ✅
const schema = z.object({ email: z.string().email('邮箱格式不正确') })
type FormValues = z.infer<typeof schema>
const { register, handleSubmit, setError, formState: { errors } } = useForm<FormValues>({
  resolver: zodResolver(schema),
  mode: 'onSubmit',
  defaultValues: { email: '' },
})
async function onSubmit(values: FormValues) {
  try {
    await createUser.mutateAsync(values)
  } catch (err) {
    if (err instanceof HttpError && err.status === 400) {
      setError('email', { message: '已被占用' })
      return
    }
    throw err
  }
}

// ❌
const [email, setEmail] = useState('')
function onSubmit() { if (!email.includes('@')) return }
useForm({ mode: 'onChange' })
```

文件输入用 `ref` 取 `FileList`，不必进 RHF 值树。
