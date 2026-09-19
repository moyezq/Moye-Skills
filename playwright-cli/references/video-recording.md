# 视频录制

把浏览器自动化过程录成视频，用于调试、文档或验收。产出 WebM（VP8/VP9）。

## 基础录制

```bash
# 先打开浏览器
playwright-cli open

# 开始录制
playwright-cli video-start demo.webm

# 在章节切换处加章节标记
playwright-cli video-chapter "Getting Started" --description="Opening the homepage" --duration=2000

# 导航并执行操作
playwright-cli goto https://example.com
playwright-cli snapshot
playwright-cli click e1

# 再加一章
playwright-cli video-chapter "Filling Form" --description="Entering test data" --duration=2000
playwright-cli fill e2 "test input"

# 停止并保存
playwright-cli video-stop
```

## 最佳实践

### 1. 用有意义的文件名

```bash
# 文件名里带上上下文
playwright-cli video-start recordings/login-flow-2024-01-15.webm
playwright-cli video-start recordings/checkout-test-run-42.webm
```

### 2. 整段「演示脚本」一起录

给用户演示或作为工作证明录视频时，最好写一段代码，用 `run-code` 执行。
这样能在动作之间插入合适停顿，并给视频加标注。Playwright 为此提供了新 API。

1) 先用 CLI 走一遍场景，记下所有 locator 与动作。后面高亮要用这些 locator 的包围盒。
2) 写好录视频用的脚本文件（见下）。打字用带 delay 的 `pressSequentially`，并留合理停顿。
3) 用 `playwright-cli run-code --filename your-script.js` 执行。

**重要**：覆盖层是 `pointer-events: none`——不会挡住页面交互。可以一直开着粘性覆盖层，同时点击、填表或做其它操作。

```js
async page => {
  await page.screencast.start({ path: 'video.webm', size: { width: 1280, height: 800 } });
  await page.goto('https://demo.playwright.dev/todomvc');

  // 显示章节卡片——模糊页面并弹出对话框。
  // 持续到 duration 结束，然后自动移除。
  // 简单场景用这个即可；也可以随时用 await page.screencast.showOverlay()
  // 手写更漂亮的覆盖层。
  await page.screencast.showChapter('Adding Todo Items', {
    description: 'We will add several items to the todo list.',
    duration: 2000,
  });

  // 执行动作
  await page.getByRole('textbox', { name: 'What needs to be done?' }).pressSequentially('Walk the dog', { delay: 60 });
  await page.getByRole('textbox', { name: 'What needs to be done?' }).press('Enter');
  await page.waitForTimeout(1000);

  // 下一章
  await page.screencast.showChapter('Verifying Results', {
    description: 'Checking the item appeared in the list.',
    duration: 2000,
  });

  // 加粘性标注，动作进行时一直显示。
  // 覆盖层是 pointer-events: none，不会挡住点击。
  const annotation = await page.screencast.showOverlay(`
    <div style="position: absolute; top: 8px; right: 8px;
      padding: 6px 12px; background: rgba(0,0,0,0.7);
      border-radius: 8px; font-size: 13px; color: white;">
      ✓ Item added successfully
    </div>
  `);

  // 标注仍可见时继续操作
  await page.getByRole('textbox', { name: 'What needs to be done?' }).pressSequentially('Buy groceries', { delay: 60 });
  await page.getByRole('textbox', { name: 'What needs to be done?' }).press('Enter');
  await page.waitForTimeout(1500);

  // 结束后移除标注
  await annotation.dispose();

  // 也可以高亮相关 locator，并加上下文标注。
  const bounds = await page.getByText('Walk the dog').boundingBox();
  await page.screencast.showOverlay(`
    <div style="position: absolute;
      top: ${bounds.y}px;
      left: ${bounds.x}px;
      width: ${bounds.width}px;
      height: ${bounds.height}px;
      border: 1px solid red;">
    </div>
    <div style="position: absolute;
      top: ${bounds.y + bounds.height + 5}px;
      left: ${bounds.x + bounds.width / 2}px;
      transform: translateX(-50%);
      padding: 6px;
      background: #808080;
      border-radius: 10px;
      font-size: 14px;
      color: white;">Check it out, it is right above this text
    </div>
  `, { duration: 2000 });

  await page.screencast.stop();
}
```

大胆发挥，覆盖层很有用。

### Overlay API 摘要

| 方法 | 用途 |
|------|------|
| `page.screencast.showChapter(title, { description?, duration?, styleSheet? })` | 全屏章节卡片 + 模糊背景——适合章节切换 |
| `page.screencast.showOverlay(html, { duration? })` | 自定义 HTML 覆盖层——标注、标签、高亮 |
| `disposable.dispose()` | 移除未设 duration 的粘性覆盖层 |
| `page.screencast.hideOverlays()` / `page.screencast.showOverlays()` | 临时隐藏/显示全部覆盖层 |

## Tracing vs 视频

| 特性 | 视频 | Tracing |
|------|------|---------|
| 产出 | WebM 文件 | Trace 文件（用 Trace Viewer 查看） |
| 展示 | 画面录制 | DOM 快照、网络、控制台、动作 |
| 场景 | 演示、文档 | 调试、分析 |
| 体积 | 较大 | 较小 |

## 限制

- 录制会给自动化带来轻微开销
- 大段录像会占较多磁盘
