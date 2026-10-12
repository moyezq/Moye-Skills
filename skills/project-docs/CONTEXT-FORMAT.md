# CONTEXT.md 格式

## 结构

```md
# {上下文名称}

{一两句：这个上下文是什么、为什么存在。}

## Language

**Order**：
{术语的一两句定义}
_Avoid_: Purchase, transaction

**Invoice**：
发货后发给客户催款的请求。
_Avoid_: Bill, payment request

**Customer**：
下单的个人或组织。
_Avoid_: Client, buyer, account
```

## 规则

- **要有主见**。一个概念有多个词时，挑最好的一个，其余列到 `_Avoid_`。
- **定义要紧凑**。一两句封顶。定义它**是**什么，不是它**做**什么。
- **只收本项目上下文特有的术语**。通用编程概念（超时、错误类型、工具模式）不属于这里，哪怕项目大量使用。加词前先问：这是本上下文独有的概念，还是通用编程概念？只有前者才收。
- **自然成簇时分小标题**。所有术语同属一个内聚领域时，平列表也行。

## 单限界上下文 vs 多限界上下文仓库

**单限界上下文（多数仓库）**：根目录一个 `CONTEXT.md`。

**多限界上下文**：根目录一个 `CONTEXT-MAP.md` 列出各上下文、它们在哪、如何关联：

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md): receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md): generates invoices and processes payments
- [Fulfillment](./src/fulfillment/CONTEXT.md): manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

skill 自行推断适用哪种结构：

- 有 `CONTEXT-MAP.md` → 读它找上下文
- 只有根 `CONTEXT.md` → 单限界上下文
- 都没有 → 第一个术语落定时用到再建根 `CONTEXT.md`

多限界上下文时推断当前话题属哪个；拿不准就问。
