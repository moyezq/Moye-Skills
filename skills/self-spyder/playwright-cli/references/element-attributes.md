# 检查元素属性

快照里看不到元素的 `id`、`class`、`data-*` 或其它 DOM 属性时，用 `eval` 检查。

## 示例

```bash
playwright-cli snapshot
# 快照把按钮标成 e7，但看不到 id 或 data 属性

# 取元素 id
playwright-cli eval "el => el.id" e7

# 取全部 CSS class
playwright-cli eval "el => el.className" e7

# 取某个属性
playwright-cli eval "el => el.getAttribute('data-testid')" e7
playwright-cli eval "el => el.getAttribute('aria-label')" e7

# 取计算样式属性
playwright-cli eval "el => getComputedStyle(el).display" e7
```
