# 运行 Playwright 测试

运行 Playwright 测试用 `npx playwright test`，或包管理器脚本。不想打开交互式 HTML 报告时，设环境变量 `PLAYWRIGHT_HTML_OPEN=never`。

```bash
# 跑全部测试
PLAYWRIGHT_HTML_OPEN=never npx playwright test

# 用自定义 npm 脚本跑全部测试
PLAYWRIGHT_HTML_OPEN=never npm run special-test-command
```

# 调试 Playwright 测试

调试失败测试时，加 `--debug=cli`。命令会在测试开头暂停，并打印调试说明。

**重要**：把命令放到后台跑，一直看到输出里出现 "Debugging Instructions"。结束后务必停掉该命令。

说明里会给出会话名，再用 `playwright-cli` attach 该会话并探索页面。

```bash
# 跑测试
PLAYWRIGHT_HTML_OPEN=never npx playwright test --debug=cli
# ...
# ... "tw-abcdef" 会话的调试说明 ...
# ...

# Attach 到测试
playwright-cli attach tw-abcdef
```

探索和找修复时，让测试继续在后台跑着。
测试在开头就暂停，所以你应单步前进，或停在最可能出问题的位置。

用 `playwright-cli` 做的每个动作都会生成对应的 Playwright TypeScript 代码。
代码会出现在输出里，可直接拷进测试。多数时候要改的是某个 locator 或断言，也可能是应用本身的 bug。自行判断。

修好测试后，停掉后台测试运行。再跑一遍确认通过。
