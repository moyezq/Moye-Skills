# Windows 外壳这一层

窗口、输入、材质、系统集成。每条都写清症状与修法；出问题时按症状查这一份。

标 `Win32` 的条目在 Electron / Tauri 里要靠原生模块或插件，在 WebView2 宿主里直接调。

## 窗口与焦点

- **标题栏整条可拖**。自定义标题栏时，整条空白区域都要能拖窗口，不是一个居中的小把手。CSS `-webkit-app-region: drag` 在 WebView2 里要先开 `IsNonClientRegionSupportEnabled`，按钮那片再单独标 `no-drag`。
- **`Ctrl-W` 关窗口，`Win+↓` 最小化**。用户在别的 Windows 程序里练出来的手会直接按，没反应就是不合手。
- **点任务栏图标回到上次那个窗口**，不是新开一个。只有「每次点击都该新开」的应用才例外。
- **窗口大小与位置跨启动记忆**，多显示器时记住它原来在哪块屏；重开时出现在当前活动屏，不是永远第 0 号屏。
- **设置开独立窗口**（`Ctrl-,` 打开），不塞进主窗口当模态。
- **确认类对话框用系统对话框**。既要打断又要保护聚焦的地方才用模态；其余先穷尽内联与渐进方案。DOM 自绘模态 + 遮罩模糊是网页。
- **失焦行为可预期**：启动器类窗口失焦即隐藏，主窗口类失焦什么都不做。选一种并保持。
- **真退出**：退干净，不留隐藏进程。

## 材质与透明（mica / acrylic）

`Win32`，Windows 11：

1. `DwmSetWindowAttribute(hwnd, DWMWA_SYSTEMBACKDROP_TYPE, DWMSBT_MAINWINDOW)` 拿 mica，`DWMSBT_TRANSIENTWINDOW` 拿 acrylic。
2. `DwmExtendFrameIntoClientArea(hwnd, MARGINS{ cyTopHeight = -1 })` 把客户区扩到整窗。
3. WebView 的背景设成全透明（WebView2：`DefaultBackgroundColor = Color.FromArgb(0,0,0,0)`）；CSS 侧 `body { background: transparent }`，让材质透上来。
4. 拖拽区、按钮命中区要自己处理，透明区域不会自动命中。

要点：

- **窗口阴影与窗口圆角交给系统**。CSS 的 `box-shadow` 与 `border-radius` 画不出系统那套（系统圆角会跟着 OS 版本变），画出来就是「贴了一层网页」。
- **材质当表面属性用，不当装饰**。mica 给主窗口，acrylic 给浮出的瞬态表面；随手给每张卡片加 `backdrop-filter` 是网页手法。
- **在 Win10、11、11 22H2、11 24H2 各测一遍**，这几版的行为有细微差别。
- **强调色跟系统**（`UISettings.GetColorValue(UIColorType.Accent)`），别硬编码品牌蓝。

## 启动不白闪

- **先建好 WebView 环境再显示窗口**。WebView2 初始化是异步的：窗口先可见、内容后到，中间那段就是白闪。
- **把默认底色设成窗口底色**，在 `EnsureCoreWebView2Async` 完成前设好；默认是白的。
- **等首次 `NavigationCompleted` 再 `Show()`**。
- 热键唤起类应用：隐藏时预热，显示时不要重新加载。

## 隐藏与后台节流

窗口最小化或被遮挡时，Chromium 会停掉定时器与渲染。要托盘图标刷新、后台取数、通知照常工作，就关掉这套节流：

```
--disable-renderer-backgrounding
--disable-background-timer-throttling
--disable-backgrounding-occluded-windows
```

WebView2 另加 `Settings.IsBackgroundResourceLoadingEnabled = true`。**真需要在隐藏时继续渲染**（少见）就保持窗口存在但整窗透明，别 `Hide()`。

## 多窗口隔离

**每种逻辑窗口用独立的 WebView 环境与独立 userDataFolder**（WebView2：每个窗口类型一个 `CoreWebView2Environment`）。设置窗口崩掉不该带走主窗口。代价是内存，换的是故障域隔离。

## 光标与选区

- **列表行、按钮、标签、侧栏项的光标保持不变**。要手型的只有真正可拖拽的句柄。这一条是「像网页」最响的信号。
- **chrome 禁选**：`user-select: none` 铺全局，内容区与可编辑区再 `user-select: text` opt-in。标题、按钮文字、标签被拖出一片蓝色，用户立刻知道这是网页。
- **I-beam 只给输入框**。非编辑区的 I-beam 同样是网页习惯。
- **chrome 上不要拼写红波浪线**，只有用户输入的文本才检查。

## 原生右键菜单

拦截 WebView 的右键（WebView2：`CoreWebView2.ContextMenuRequested`），换成原生菜单项：复制 / 粘贴 / 全选 / 在资源管理器中显示 / 应用自己的动作。删掉「重新加载」「检查元素」这类浏览器项。

判定：右键点在输入框里要出系统的编辑菜单，点在列表项上要出应用的动作菜单。Chromium 默认那套一律不要。

## IME 输入法

中文拼音是最吃紧的组合（快速输入 + 组字 + 候选选择）。

- **候选框要贴在插入符旁边**，不是飘在 WebView 顶上或窗口角。
- **自定义标题栏不抢焦点**：`Focusable = false`，否则拼音打到一半焦点跑掉。
- **测三种**：拼音、日文假名、韩文。
- 组字期间不要重渲染输入框的 value，会出重字或丢字。

## 滚动

- **Win11 用细滚动条**。允许自绘，但必须保住原生行为：滚轮、键盘翻页、中键、拖拽选择都要照常。
- **程序化滚动用 `behavior: 'auto'`**。平滑滚动在网页上像加分项，在桌面程序里像卡顿。
- **内层滚动区加 `overscroll-behavior: contain`**，别让滚动穿透到外层。
- **同窗口内导航不要重置滚动位置**，把上一个位置的恢复做对。
- 长列表（1000 项以上）虚拟滚动或分页，别一次渲染。

## 键盘

- **每个可操作元素都能 Tab 到**，Tab 顺序按视觉顺序而非 DOM 顺序。
- **焦点环可见且跟系统样式**。用户在自己别的程序里认的就是这个环。
- **`Ctrl-F` 查找、`Ctrl-,` 设置、`Ctrl-W` 关闭**，跟 Windows 惯例对齐。
- **`Esc` 永远有作用**：关浮层、取消当前动作、收起窗口。什么都不做是最差的一种。
- **列表支持 type-ahead**：敲字母跳到匹配项。
- **主流程不用鼠标能走完**。

## 拖放与剪贴板

- **走真实文件路径的拖放**，不是网页那套 File 对象。拖到任务栏图标上也要能打开。
- **剪贴板写全格式**：纯文本 + RTF + HTML，富内容复制到 Word 里才不掉样式。
- **保存走系统保存对话框**，不是浏览器下载条。

## 系统集成

- **单一实例**：第二次启动聚焦已有实例。Electron 用 `requestSingleInstanceLock`，Tauri 内置，WebView2 宿主自己写。Windows 不替你管这件事。
- **托盘图标跟随系统主题**（深浅色两套），别用彩色图标硬顶。
- **全局热键首次启动即生效**，不需要用户重启或重注册。
- **开机自启要用户主动勾选**，不静默加。
- **真自动更新**（MSIX 或自建更新流程），不是弹个「请去下载新版本」的链接。
- **崩溃上报接真服务**，能拿到符号化堆栈。
- **注册 URL scheme 与文件关联**：`appname://` 全系统可用，双击关联文件能打开应用。
- **应用清单正确**：标识符、版本、图标、文档类型。
- **任务栏图标是自己的图标**，不是 Electron 默认那个。

## 无障碍

- **Narrator 能走完整个界面**：WebView 内容要有正确的 ARIA 角色与可访问名，图标按钮尤其不能只有图形。
- **焦点移动要有播报**。
- **对比度达 WCAG AA**（正文 ≥4.5:1，大字与控件 ≥3:1）。
- **系统字号放大到 200% 不破版**：不要用固定像素锁死容器高。
- **Windows 高对比模式要测过**：`forced-colors` 下不要只剩一片黑。
- **不靠颜色单独传信息**，再补文字、形状或位置。
- **所有动作都能不用鼠标完成**。
