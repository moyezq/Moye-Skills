# 目录与工程配置

命中「目录树、别名、环境变量、同仓 frontend/、加一个 feature」时读本文。新建项目先走 [scaffold.md](./scaffold.md)。

完成标准：新文件落在下表对应目录；一个 feature 具备 api / keys / hook / 页面；导入走 `@/`；前端环境变量以 `VITE_` 开头。

## 何时用

**用**：新建或整理前端目录；加 feature / 路由 / store；改 Vite 配置、别名、代理、`.env`。

**不用**：只改某个组件内部。只改 Query / Zustand 用法——见 [data.md](./data.md)。

## 目录树

结构只画这一次。纯前端仓把 `src/` 放仓根；前后端同仓把下面整棵放到 `frontend/`。

```text
src/
  app/              提供者、router、路由级错误 UI、根布局
  routes/           路由页面（薄，组装 feature）
  features/<name>/  一个业务模块
    api.ts
    <name>-keys.ts
    use-<name>.ts
    XxxList.tsx
    XxxForm.tsx
    XxxList.test.tsx
  components/ui/    仅 shadcn 生成
  components/       跨 feature 的包装组件
  hooks/            跨 feature 的 hooks
  lib/              http、query-client、cn
  stores/           Zustand store，一个领域一个文件
  test/             Vitest setup
  main.tsx
  index.css
```

```text
# ✅
features/orders/api.ts
features/orders/use-orders.ts
features/orders/OrderList.tsx
routes/OrderListPage.tsx

# ❌
src/pages/user/list/index.tsx
src/services/userService.ts
src/utils/index.ts
src/features/orders/index.ts
src/components/ui/button.tsx   里改 shadcn 源码
```

- 路由页只负责壳：读 `useParams` / `useSearchParams`，调用 `useOrders`，摆 `isPending` / 空 / 错 / 列表。
- feature 专属组件放在该 feature 目录，不放到全局 `components/`。
- 测试与源文件同目录。
- 不写 `index.ts` 桶文件（本栈已锁）。复杂 UI 可以建 `components/UserCard/UserCard.tsx`，导入仍写到文件。

已有仓目录与上树不一致：新文件仍按上树放；不把邻居文件挪过来（R11）。

## 别名

`@` 指向该前端包的 `src/`。`tsconfig.app.json` 与 `vite.config.ts` 都要写。

```ts
import { http } from '@/lib/http'
```

```ts
import { http } from '../../../lib/http'
```

## 环境变量与代理

- 只有 `VITE_` 前缀能进客户端。密钥不进 `VITE_`。
- 开发时 `VITE_API_BASE` 留空，请求走相对路径 `/api/...`，Vite 把 `/api` 代理到 `http://127.0.0.1:8000`。
- 生产要直连网关时再设 `VITE_API_BASE`。

```ts
// ✅
const base = import.meta.env.VITE_API_BASE ?? ''

// ❌
const base = process.env.API_URL
const token = import.meta.env.VITE_SECRET_KEY
```
