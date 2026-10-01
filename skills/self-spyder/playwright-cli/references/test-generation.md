# 测试生成（plan → generate → heal）

用 `playwright-cli` 编写与维护 Playwright 测试的端到端流程。每次 `playwright-cli` 动作都会吐出等价的 Playwright TypeScript，这些生成代码是一切测试的原材料。下面各节可独立使用：

- **生成机制** — 其它一切依赖的核心：动作变成 TypeScript，以及如何加断言。
- **Plan** — 探索应用，产出描述测什么的 spec 文件。
- **Generate** — 把 spec 变成 Playwright 测试文件。spec 含糊或过期时先更新。
- **Heal** — 诊断失败测试、修代码，并把 spec 与现实对齐。

Plan / generate / heal 共用同一机制：后台跑 `npx playwright test --debug=cli`，再用 `playwright-cli attach tw-XXXX` 交互驱动暂停中的页面。调试 / attach 细节见 [playwright-tests.md](playwright-tests.md)。

**生成测试的顺序**：先按场景逐步点完（`playwright-cli` 动作 + snapshot），再根据这次操作历史写测试文件；测试里的每个 action 都对应会话里一次真实操作。

---

## 0. 生成机制

用 `playwright-cli` 做的每个动作都会生成对应的 Playwright TypeScript。代码出现在输出里，可直接拷进测试文件。

```bash
# 开启会话
playwright-cli open https://example.com/login

# 拍快照看元素
playwright-cli snapshot
# 输出类似：e1 [textbox "Email"], e2 [textbox "Password"], e3 [button "Sign In"]

# 填表单——自动生成代码
playwright-cli fill e1 "user@example.com"
# Ran Playwright code:
# await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

playwright-cli fill e2 "password123"
# Ran Playwright code:
# await page.getByRole('textbox', { name: 'Password' }).fill('password123');

playwright-cli click e3
# Ran Playwright code:
# await page.getByRole('button', { name: 'Sign In' }).click();
```

### 拼成测试文件

把生成代码收进 Playwright 测试：

```typescript
import { test, expect } from '@playwright/test';

test('login flow', async ({ page }) => {
  // 来自 playwright-cli 会话的生成代码：
  await page.goto('https://example.com/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();

  // 自行加断言
  await expect(page).toHaveURL(/.*dashboard/);
});
```

### 优先用语义 locator

生成代码在可能时使用基于 role 的 locator，更抗变更：

```typescript
// 生成结果（好——语义化）
await page.getByRole('button', { name: 'Submit' }).click();

// 避免（脆——CSS 选择器）
await page.locator('#submit-btn').click();
```

### 录制前先探索

录动作前先拍快照，弄清页面结构：

```bash
playwright-cli open https://example.com
playwright-cli snapshot
# 先看清元素结构
playwright-cli click e5
```

### 断言要手动加

生成代码只捕获动作，不捕获断言。在测试里用下列推荐 matcher 加期望：

- `toBeVisible()` — 元素已渲染且可见
- `toHaveText(text)` — 元素文本匹配
- `toHaveValue(value) / toBeEmpty()` — input/select 值匹配
- `toBeChecked() / toBeUnchecked()` — 复选框状态匹配
- `toMatchAriaSnapshot(snapshot)` — 页面（或 locator）匹配部分无障碍快照

用 `playwright-cli generate-locator <target>` 生成断言用的 locator 表达式；用 snapshot/eval 抓期望值。

断言文本内容时，确保生成的 locator **不要**带上元素自身文本。`getByTestId()` 或 `getByLabel()` 通常更适合配合文本断言。若 locator 本身基于文本，优先用 `toBeVisible()`。

要匹配的快照不必包含全部信息——只抓断言需要的部分。不稳定值可用正则。

```bash
# 为元素 ref 生成稳定 locator，用于断言
playwright-cli --raw generate-locator e5
# getByRole('button', { name: 'Submit' })

# 抓 toHaveText 的期望文本
playwright-cli --raw eval "el => el.textContent" e5

# 抓 toHaveValue/toBeEmpty 的期望输入值
playwright-cli --raw eval "el => el.value" e5

# 抓 toMatchAriaSnapshot/toBeChecked 用的 aria 快照
# （整页，或用 ref 限定区域）
playwright-cli --raw snapshot
playwright-cli --raw snapshot e5
```

```typescript
// 生成的动作
await page.getByRole('button', { name: 'Submit' }).click();

// 用上面输出手写断言：
await expect(page.getByRole('alert', { name: 'Success' })).toBeVisible();
await expect(page.getByTestId('main-header')).toHaveText('Welcome, user');
await expect(page.getByRole('textbox', { name: 'Email' })).toHaveValue('user@example.com');
await expect(page.getByRole('checkbox', { name: 'Enable notifications' })).toBeChecked();

// 整页 toMatchAriaSnapshot，会找匹配区域
await expect(page).toMatchAriaSnapshot(`
  - heading "Welcome, user"
  - link /\\d+ new messages?/
  - button "Sign out"
`);

// 限定到某区域的 toMatchAriaSnapshot
await expect(page.getByRole('navigation')).toMatchAriaSnapshot(`
  - link "Home"
  - link /\\d+ new messages?/
  - link "Profile"
`);
```

---

## 1. Planning

目标：产出 spec 文件（如 `specs/<feature>.plan.md`），枚举要测的场景。**必须**把 spec 写到文件。

### 1.1 前置：工作区

其它事之前先确认工作区已装 Playwright：

```bash
# 下面任一方式可确认工作区：
test -f playwright.config.ts || test -f playwright.config.js
npx --no-install playwright --version
```

若没有 Playwright，先初始化，让用户选默认项：

```bash
npm init playwright@latest
```

### 1.2 前置：seed 测试

**seed 测试**是最小测试，把页面带到每个场景的起点状态：打开应用、必要登录、feature flags 等。场景假定从 seed **之后**的干净起点开始。`--debug=cli` 会在这个测试**内部**暂停，因此每次规划与生成会话都从 seed 开始。

最小可用 seed：

```ts
// tests/seed.spec.ts
import { test } from '@playwright/test';

test('seed', async ({ page }) => {
  await page.goto('https://example.com/');
});
```

更推荐——把导航放进 fixture，场景测试复用：

```ts
// tests/fixtures.ts
import { test as baseTest } from '@playwright/test';
export { expect } from '@playwright/test';

export const test = baseTest.extend({
  page: async ({ page }, use) => {
    await page.goto('https://example.com/');
    await use(page);
  },
});
```

```ts
// tests/seed.spec.ts
import { test } from './fixtures';

test('seed', async ({ page }) => {
  // Fixture 已完成导航。空 body 告诉 agent 从这里开始。
});
```

若还没有 seed，至少建一个会导航到应用的 seed。

### 1.3 探索应用

经 seed 在后台启动应用并 attach：

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test tests/seed.spec.ts --debug=cli
# 等到 "Debugging Instructions" 与会话名 tw-XXXX
playwright-cli attach tw-XXXX
```

resume 让 seed 跑完，再探测应用：

```bash
playwright-cli resume                   # resume，让 seed 完整跑完
playwright-cli snapshot                 # 交互元素清单
playwright-cli click e5                 # 跟一条流程
playwright-cli eval "location.href"     # 读 URL / 状态
playwright-cli show --annotate          # 请用户指出某处
```

摸清：

- 交互面（表单、按钮、列表、筛选、弹层）
- 端到端主用户旅程
- 边界：空态、校验错误、超长输入、边界值
- 持久化：刷新、local/session storage、URL fragment
- 导航：哪些控件改 URL、前进/后退行为

**重要**：不要只用 playwright-cli 直接打开应用 URL；务必经测试走，才能带上测试里的自定义 setup。
**重要**：探索结束后停掉后台测试。

### 1.4 写 spec 文件

保存到 `specs/<feature>.plan.md`。结构如下：

```markdown
# <Feature> Test Plan

## Application Overview

<一段话：功能做什么、为什么重要。>

## Test Scenarios

### 1. <Group Name>

**Seed:** `tests/seed.spec.ts`

#### 1.1. <kebab-case-scenario-name>

**File:** `tests/<group>/<kebab-case-scenario-name>.spec.ts`

**Steps:**
  1. <具体用户步骤>
    - expect: <可观察结果>
    - expect: <另一可观察结果>
  2. <下一步>
    - expect: <结果>

#### 1.2. <next-scenario>
...

### 2. <Next Group>

**Seed:** `tests/seed.spec.ts`
...
```

指引：

- 每个场景独立，从 seed 的干净状态开始——绝不串场景。
- 场景名用 kebab-case，并与测试文件名一致（`should-add-single-todo` → `should-add-single-todo.spec.ts`）。
- 覆盖 happy path、边界、校验、负面流程、持久化。
- 步骤写用户层（「在输入框输入 Buy milk」），不要写 API 层（「调用 fill」）。
- 可观察结果放在 `- expect:` 条目；生成时每条变成一条断言。

---

## 2. Generate

目标：根据 spec 产出 Playwright 测试文件。spec 漂移时可顺便更新。

### 2.1 输入

- **Spec 文件**，如 `specs/basic-operations.plan.md`。
- **目标**：单个场景（如 `1.2`）、整组（`1`），或全部。
- **Seed 文件**：读该场景所属组的 `**Seed:**` 行。

### 2.2 生成单个场景

对每个目标场景按顺序处理（不要并行——场景共享 seed 会话）：

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test <seed-file> --debug=cli   # 后台
playwright-cli attach tw-XXXX
# resume
```

**不要**只用 playwright-cli 直接打开应用 URL；务必经测试走，才能带上测试里的自定义 setup。

按场景的 `Steps:` 逐步用 `playwright-cli` 走，把 spec 当计划、把实况应用当真相源。若某步含糊（「点那个按钮」——哪个？）、引用已不存在的元素，或与应用真实行为矛盾，自行判断：把 spec 改成与应用一致，然后继续。生成中途改 spec 是正常的。

每个动作都会打印等价 Playwright TypeScript（见 [生成机制](#0-生成机制)）：

```bash
playwright-cli snapshot                         # 找 ref
playwright-cli fill e3 "John Doe"               # -> page.getByRole('textbox', {...}).fill(...)
playwright-cli press Enter
playwright-cli click e7
```

每条 `- expect:` 都要加显式断言。细节见 [生成机制](#0-生成机制)。

收齐生成代码，写到 spec 给出的路径：

```ts
// spec: specs/basic-operations.plan.md
// seed: tests/seed.spec.ts
import { test, expect } from './fixtures';   // 无 fixtures 文件则用 '@playwright/test'

test.describe('Signing in and out', () => {
  test('should sign in', async ({ page }) => {
    // 1. Navigate to the application
    // （由 seed fixture 处理）

    // 2. Type 'John Doe' into the username field
    await page.getByRole('textbox', { name: 'username' }).fill('John Doe');

    // 3. Type password
    await page.getByRole('textbox', { name: 'password' }).fill('TestPassword');

    // 4. Press Enter to submit
    await page.getByRole('textbox', { name: 'password' }).press('Enter');

    await expect(page.getByRole('heading')).toContainText('Welcome, John Doe!');
  });
});
```

规则：

- **一文件一测。** 文件路径、describe 名、test 名直接来自 spec（去掉序号）。
- 每个编号步骤前加 `// N. <步骤原文>` 注释，再写动作。
- describe 组名用 spec 原文（不要带 `1.` 序号）。
- 项目有 `./fixtures` 就从那里 import；否则 `@playwright/test`。
- **重要**：进入下一场景前，关掉 CLI 会话并停掉后台测试。

### 2.3 生成多个场景

对目标场景逐个循环 2.2，场景之间重启 seed，保证每个测试从干净页面开始。因会话名唯一，可并行——但务必停掉每次测试运行。

### 2.4 跑生成的测试

生成后跑一遍新测试：

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test tests/<group>/<scenario>.spec.ts
```

有失败就进第 3 节。

---

## 3. Heal

目标：修好失败测试；若应用预期行为已变，同步更新 spec。

### 3.1 找出失败测试

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test
```

记下失败的 `<file>:<line>` 列表，一次处理一个。不要并行修——共享状态与单一 CLI 会话会很脆。

### 3.2 调试单个失败

后台以 debug 模式跑单个失败测试，再 attach：

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test tests/<group>/<scenario>.spec.ts:<line> --debug=cli
# 等到 "Debugging Instructions" 与 tw-XXXX 会话名
playwright-cli attach tw-XXXX
```

测试在开头暂停。前进或跑到失败动作/断言之前，再诊断：

```bash
playwright-cli snapshot                # 元素是否变了 / 挪了 / 改名了？
playwright-cli console                 # 应用侧错误？
playwright-cli requests                # 请求失败？payload 错了？
playwright-cli show --annotate         # 请用户指出某处
```

常见原因：选择器漂移、新包了一层元素、label/ARIA 改名、时序（过渡、异步加载）、应用改了断言文本、测试数据跨次泄漏。

用 `playwright-cli` 排练修正后的交互——输出里的生成代码就是要贴回测试的内容。

### 3.3 落地修复

改测试文件：更新 locator、断言、步骤顺序或输入，与正确行为一致。停掉后台 debug 运行。单测重跑确认变绿。

不要用跳过 hook 或加 sleep 当修复。不要用 `networkidle`。

### 3.4 与 spec 对齐

打开测试文件里 `// spec:` 指向的 spec，找到对应该测的场景。

- **纯技术修复**（locator 漂移、更好的断言形状），且 spec 的用户层行为仍与应用一致 → 不动 spec。
- **修复改了用户可见的步骤、输入、顺序或期望结果**，而 spec 还写着旧的 → 更新 spec 以匹配现实。保持场景 id 与文件路径不变；只改 step / expect 行。
- **分不清是应用有意变更**（spec 过期）**还是回归**（测试对、应用错）→ **停下问用户**。提供：
  - 场景 id（如 `2.3`），
  - 已不再匹配的 spec 行，
  - 观察到的应用行为（引用快照片段或具体结果）。

等用户答复后，再要么更新 spec（有意变更），要么把测试标成覆盖某个 bug（回归）。

### 3.5 迭代与放弃

- 一次修一个失败；每次修完重跑。
- 若充分调查后确信测试正确、应用有错，**且**用户确认是 bug：用 `test.fixme(...)` 标出，并注释指向用户决定或 issue 链接。绝不静默 skip。

---

## 交叉引用

| 需求 | 参见 |
|------|------|
| `--debug=cli` / attach 机制 | [playwright-tests.md](playwright-tests.md) |
| 探索/生成时的请求 Mock | [request-mocking.md](request-mocking.md) |
| 管理 CLI 浏览器会话 | [session-management.md](session-management.md) |
