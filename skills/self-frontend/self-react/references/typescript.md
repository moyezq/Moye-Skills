# React 中的 TypeScript

`self-react` 的披露参考：写或改 `.ts` / `.tsx`、镜像类型、API 模块类型时读。布局 CSS 与界面验收仍在 `SKILL.md`。

完成标准：改到的 `.ts` / `.tsx` 没有 `any`；API 返回值与组件 props 都是具名类型；改了契约则前后端镜像字段对齐；互斥变体的 `switch` 有 `never` 穷尽。逐条都做到才算完成。

类型检查命令见 `SKILL.md` 门禁。本文件要求 tsconfig 开 `strict` + `noUnusedLocals` + `noUnusedParameters`。契约怎么钉见 `self-python-function`。

## 镜像类型

后端契约字段在前端有一份**同名镜像类型**，字段逐个对齐。契约改名，前端同一次改完。契约是单一事实源，镜像只跟随：不发明字段、不改名、不另起一套。

类型跟拥有它的模块走：镜像类型放 API 模块；只服务一个组件的 props 与局部状态跟该组件同文件；多模块共用的形状放拥有该概念的模块。

响应里字段稳定、含义固定的部分（枚举、必填 id）用字面量或联合类型写死。

互斥变体用带 `kind` 字面量的判别联合，不用 optional 字段袋；`switch` 的 `default` 写 `const _: never = x` 做穷尽检查。

`fetch` / JSON 的入口是 `unknown`。在 API 模块里收窄成镜像类型，结果赋给具名变量再返回。组件只调用这些函数。

## 命名

组件与类型用名词 PascalCase（`UserCard`、`LoadState`）。函数用动词或 `is` / `has` / `can` 谓词 camelCase（`loadUser`、`isReady`）。子组件回调 props 用 `on` + 事件（`onSubmit`）。
