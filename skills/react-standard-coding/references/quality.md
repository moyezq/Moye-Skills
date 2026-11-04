# 测试与代码风格工具

命中「写组件测试、改 ESLint / Prettier / Vitest 配置」时读本文。E2E 点选走查不写在本 skill。

完成标准：新的交互组件有一条 RTL 测试，或本次改动是纯样式 / 纯类型则明确不测；`pnpm test` 与 ESLint 配置在前端包内可运行。

## 何时用

**用**：给组件或 `http` 的纯函数补测试；改 `vite.config.ts` 的 `test` 段；改 ESLint / Prettier。

**不用**：第一次搭项目（脚手架已接 Vitest）。只改文案。浏览器里点一遍页面当验收——那是人做的，Agent 不替用户起 Vite。

## Vitest + RTL

- 测试文件与源文件同目录，名为 `Xxx.test.tsx`。
- 测用户能看见和点到的行为。查询优先 `getByRole` / `getByLabelText`，不要 `getByTestId`。
- 不测组件内部 state 变量名。
- 用到 Query 的组件：测试里包 `QueryClientProvider`，`retry: false`。
- 网络用 `http` 的 mock 或 `queryClient.setQueryData`，不在测试里真发请求。

```tsx
// ✅
import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { StatusBadge } from './StatusBadge'

test('shows label', () => {
  render(<StatusBadge label="在线" tone="ok" />)
  expect(screen.getByText('在线')).toBeInTheDocument()
})

// ❌
test('state is true', () => {
  const { result } = renderHook(() => useToggle())
  expect(result.current.on).toBe(false)
})
test('has node', () => {
  render(<StatusBadge label="在线" tone="ok" />)
  expect(document.querySelector('.badge')).toBeTruthy()
})
```

跑法（在前端包目录）：

```powershell
pnpm test
```

失败时看第一条失败断言，不要加 `--watch` 常驻。

## ESLint 与 Prettier

- 沿用 Vite 模板的 ESLint flat config，不换 Biome。
- Prettier 只管格式；ESLint 不管 `indent` / `quotes`。
- 不装 Husky、lint-staged、commitlint。格式化靠编辑器与 CI 命令，不靠 Git hook。
