# 新建 Vite React 项目

命中「新建 Vite React 项目、第一次搭本栈」时读本文。目录落点见 [project.md](./project.md)。写法见 [write.md](./write.md)。请求与状态见 [data.md](./data.md)。

完成标准：目标目录里有 `src/app/router.tsx`、`src/lib/http.ts`、Tailwind、shadcn 的 `components.json`；`package.json` 含锁死技术栈里的运行时依赖。脚本失败时用户拿到从失败步起的手搓命令，Agent 不再跑脚本。

## 何时用

**用**：仓库还没有本栈前端，或用户明确说「新建 React 项目」。

**不用**：已有 `src/app/router.tsx`（已经搭过）。只加一个页面或组件。旧仓技术栈不一致时按全局 R11，不在这里推倒重来。

## 目标目录

1. 仓根已有 Python 后端痕迹（`pyproject.toml`、或 `main.py` 加 `requirements.txt` / `conf/`）→ 前端放 `frontend/`
2. 仓根已有带 `react` 的 `package.json` → 就在仓根
3. 其余 → 仓根（纯前端仓）

## 脚本只跑一次

对本仓库、本会话，`scripts/scaffold.py` **只调用一次**。

```powershell
python "<skill根目录>/scripts/scaffold.py" --project-root "<仓根>"
```

覆盖自动落点时才加 `--target frontend` 或 `--target root`。

- 退出码 0 → 按 [project.md](./project.md) 核对目录，开始写业务代码。不要起 Vite 常驻进程。
- 退出码非 0 → **立刻停**。把脚本打印的「请用户手动执行」命令交给用户。禁止改参数再跑脚本，禁止拆成多步自己重试 `pnpm create` / `shadcn init`。

```text
# ✅ 跑一次，失败就把命令交给用户
python .../scaffold.py --project-root E:\proj

# ❌ 失败后再跑第二次、或改 --target 重跑
```

## 默认会装的依赖

运行时：`react-router-dom`、`zustand`、`@tanstack/react-query`、`react-hook-form`、`@hookform/resolvers`、`zod`、`react-error-boundary`、`lucide-react`

样式：`tailwindcss`、`@tailwindcss/vite`、shadcn（`init --yes`，再 `add button --yes`）

开发：`vitest`、`@testing-library/react`、`@testing-library/jest-dom`、`jsdom`、`prettier`、`@types/node`

动画、i18n、dnd-kit、Husky 不装。用户点名再走 [ondemand.md](./ondemand.md)。
