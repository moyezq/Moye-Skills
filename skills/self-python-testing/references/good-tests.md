# 好测试与坏测试

## 好测试

**集成风格（integration-style）**：通过真实接口测试，而不是对内部部件做 mock。

```python
# GOOD: Tests observable behavior
def test_user_can_checkout_with_valid_cart():
    cart = create_cart()
    cart.add(product)
    result = checkout(cart, payment_method)
    assert result.status == "confirmed"
```

特征：

- 测的是用户/调用方在意的行为
- 只用公开 API
- 能扛住内部重构
- 描述的是「是什么（WHAT）」，而不是「怎么做（HOW）」
- 每个测试只有一个逻辑断言

## 坏测试

**实现细节测试（implementation-detail tests）**：与内部结构耦合。

```python
from unittest.mock import patch

# BAD: Tests implementation details
def test_checkout_calls_payment_service_process():
    with patch("checkout.payment_service") as mock_payment:
        checkout(cart, payment)
    mock_payment.process.assert_called_once_with(cart.total)
```

危险信号：

- mock 内部协作者
- 测试私有方法
- 对调用次数/顺序做断言
- 重构了但行为没变，测试却挂了
- 测试名描述的是 HOW 而不是 WHAT
- 通过外部手段而不是接口来验证

```python
# BAD: Bypasses interface to verify
def test_create_user_saves_to_database():
    create_user(name="Alice")
    row = db.query("SELECT * FROM users WHERE name = ?", ["Alice"])
    assert row is not None

# GOOD: Verifies through interface
def test_create_user_makes_user_retrievable():
    user = create_user(name="Alice")
    retrieved = get_user(user.id)
    assert retrieved.name == "Alice"
```

**同义反复测试（tautological tests）**：期望值只是把实现重述一遍，于是测试按构造就通过。

```python
# BAD: Expected value is recomputed the way the code computes it
def test_calculate_total_recomputes_expected():
    items = [{"price": 10}, {"price": 5}]
    expected = sum(item["price"] for item in items)
    assert calculate_total(items) == expected

# GOOD: Expected value is an independent, known literal
def test_calculate_total_sums_line_items():
    assert calculate_total([{"price": 10}, {"price": 5}]) == 15
```
