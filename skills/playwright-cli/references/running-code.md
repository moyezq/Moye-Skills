# 运行自定义 Playwright 代码

CLI 命令覆盖不到的高级场景，用 `run-code` 执行任意 Playwright 代码。

## 语法

```bash
playwright-cli run-code "async page => {
  // 在此写 Playwright 代码
  // 用 page.context() 做浏览器上下文操作
}"
```

也可以从文件加载函数：

```bash
playwright-cli run-code --filename=./my-script.js
```

代码必须是单个函数表达式，外层会包 `(...)` 再求值。
不支持 import/export/require 语法。

## 地理位置

```bash
# 授予定位权限并设置位置
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 37.7749, longitude: -122.4194 });
}"

# 设为伦敦
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 51.5074, longitude: -0.1278 });
}"

# 清除地理位置覆盖
playwright-cli run-code "async page => {
  await page.context().clearPermissions();
}"
```

## 权限

```bash
# 授予多项权限
playwright-cli run-code "async page => {
  await page.context().grantPermissions([
    'geolocation',
    'notifications',
    'camera',
    'microphone'
  ]);
}"

# 为特定源授予权限
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['clipboard-read'], {
    origin: 'https://example.com'
  });
}"
```

## 媒体模拟

```bash
# 模拟深色配色
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'dark' });
}"

# 模拟浅色配色
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'light' });
}"

# 模拟减少动效
playwright-cli run-code "async page => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
}"

# 模拟打印媒体
playwright-cli run-code "async page => {
  await page.emulateMedia({ media: 'print' });
}"
```

## 等待策略

```bash
# 等待网络空闲
playwright-cli run-code "async page => {
  await page.waitForLoadState('networkidle');
}"

# 等待特定元素
playwright-cli run-code "async page => {
  await page.locator('.loading').waitFor({ state: 'hidden' });
}"

# 等待函数返回 true
playwright-cli run-code "async page => {
  await page.waitForFunction(() => window.appReady === true);
}"

# 带超时等待
playwright-cli run-code "async page => {
  await page.locator('.result').waitFor({ timeout: 10000 });
}"
```

## Frame 与 iframe

```bash
# 操作 iframe
playwright-cli run-code "async page => {
  const frame = page.locator('iframe#my-iframe').contentFrame();
  await frame.locator('button').click();
}"

# 获取全部 frame
playwright-cli run-code "async page => {
  const frames = page.frames();
  return frames.map(f => f.url());
}"
```

## 文件下载

```bash
# 处理文件下载
playwright-cli run-code "async page => {
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download' }).click();
  const download = await downloadPromise;
  await download.saveAs('./downloaded-file.pdf');
  return download.suggestedFilename();
}"
```

## 剪贴板

```bash
# 读剪贴板（需权限）
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['clipboard-read']);
  return await page.evaluate(() => navigator.clipboard.readText());
}"

# 写剪贴板
playwright-cli run-code "async page => {
  await page.evaluate(text => navigator.clipboard.writeText(text), 'Hello clipboard!');
}"
```

## 页面信息

```bash
# 获取页面标题
playwright-cli run-code "async page => {
  return await page.title();
}"

# 获取当前 URL
playwright-cli run-code "async page => {
  return page.url();
}"

# 获取页面内容
playwright-cli run-code "async page => {
  return await page.content();
}"

# 获取视口大小
playwright-cli run-code "async page => {
  return page.viewportSize();
}"
```

## 执行 JavaScript

```bash
# 执行 JS 并返回结果
playwright-cli run-code "async page => {
  return await page.evaluate(() => {
    return {
      userAgent: navigator.userAgent,
      language: navigator.language,
      cookiesEnabled: navigator.cookieEnabled
    };
  });
}"

# 向 evaluate 传参
playwright-cli run-code "async page => {
  const multiplier = 5;
  return await page.evaluate(m => document.querySelectorAll('li').length * m, multiplier);
}"
```

## 在页面加载前注入（桩数据、mock、全局钩子）

**要在 `goto` 之前生效的注入一律用 `addInitScript`，不要用 `page.evaluate`。** `page.evaluate` 是一次性执行：它设好的 `window.*` 会被随后的页面加载覆盖成 undefined，被测页面于是白屏或报「某方法不存在」。更坏的是这个现象**看起来像被测应用自己启动失败**，容易把人带去排查应用。

```bash
playwright-cli run-code "async page => {
  await page.context().addInitScript((stub) => {
    window.__stub = stub;
  }, { api: 'http://localhost:3000' });
  await page.goto('http://127.0.0.1:8080/');
  return await page.title();
}"
```

两条容易再踩的：

- `addInitScript` 的**第一个参数必须是函数**，注入的数据是它的实参（第二项）。把 JSON 直接插到形参位置上会报 `Invalid destructuring assignment target` 这类语法错，看起来像 CLI 或脚本坏了。
- `addInitScript` **每次导航都会重跑**，`reload()` 也算。所以「只在第一次导航清一次存储」这类初始化不能无条件写在里面——第二次跑会把你前一步刚存下的状态擦掉，于是「刷新后是否记住」永远验不过（假失败）。用 `sessionStorage` 放一个记号，只清一次：

```javascript
try {
  if (!window.sessionStorage.getItem('probe-started')) {
    window.localStorage.clear();
    window.sessionStorage.setItem('probe-started', '1');
  }
} catch (e) {}
```

## 错误处理

```bash
# 在 run-code 里 try-catch
playwright-cli run-code "async page => {
  try {
    await page.getByRole('button', { name: 'Submit' }).click({ timeout: 1000 });
    return 'clicked';
  } catch (e) {
    return 'element not found';
  }
}"
```

## 复杂流程

```bash
# 登录并保存状态
playwright-cli run-code "async page => {
  await page.goto('https://example.com/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('secret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('**/dashboard');
  await page.context().storageState({ path: 'auth.json' });
  return 'Login successful';
}"

# 从多页抓取数据
playwright-cli run-code "async page => {
  const results = [];
  for (let i = 1; i <= 3; i++) {
    await page.goto(\`https://example.com/page/\${i}\`);
    const items = await page.locator('.item').allTextContents();
    results.push(...items);
  }
  return results;
}"
```
