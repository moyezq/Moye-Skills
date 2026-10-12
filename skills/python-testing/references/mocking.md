# 什么时候该 mock

只在**系统边界**上 mock：

- 外部 API（支付、邮件等）
- 数据库（有时候 —— 优先用测试数据库）
- 时间/随机性
- 文件系统（有时候）

不要 mock：

- 你自己的类/模块
- 内部依赖
- 任何你能控制的东西

## 为可 mock 性做设计

在系统边界上，把接口设计得容易 mock：

**1. 使用依赖注入**

把外部依赖传进来，而不是在内部创建它们：

```python
# Easy to mock: the dependency is passed in
def process_payment(order, payment_client):
    return payment_client.charge(order.total)

# Hard to mock: the dependency is created inside, tests cannot swap it
def process_payment_with_internal_client(order):
    client = StripeClient(os.environ["STRIPE_KEY"])
    return client.charge(order.total)
```

**2. 优先用 SDK 风格的接口，而不是通用的抓取函数**

为每个外部操作创建专门的函数，而不是用一个带条件逻辑的通用函数：

```python
# GOOD: Each method is independently mockable
class ApiClient:
    def get_user(self, user_id):
        return self._get(f"/users/{user_id}")

    def get_orders(self, user_id):
        return self._get(f"/users/{user_id}/orders")

    def create_order(self, data):
        return self._post("/orders", json=data)

# BAD: Mocking requires conditional logic inside the mock
class GenericApiClient:
    def fetch(self, endpoint, options=None):
        return self._request(endpoint, options)
```

SDK 这种做法意味着：
- 每个 mock 只返回一种特定的接口形态
- 测试准备里没有条件逻辑
- 更容易看出一个测试用到了哪些端点
- 每个端点的返回类型都能标注出来
