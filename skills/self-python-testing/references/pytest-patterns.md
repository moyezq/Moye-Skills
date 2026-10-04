# Python 测试模式

使用 pytest、fixture、mock、参数化（parameterization）以及测试驱动开发实践，在 Python 中实施稳健测试策略的全面指南。

## 何时使用本 Skill

- 为 Python 代码编写单元测试
- 搭建测试套件与测试基础设施
- 实施测试驱动开发（TDD）
- 为 API 与服务编写集成测试
- mock 外部依赖与服务
- 测试异步代码与并发操作
- 在 CI/CD 中设置持续测试
- 实施基于属性的测试（property-based testing）
- 测试数据库操作
- 调试失败的测试

## 核心概念

### 1. 测试类型

- **单元测试（Unit Tests）**：在隔离状态下测试单个函数/类
- **集成测试（Integration Tests）**：测试组件之间的交互
- **功能测试（Functional Tests）**：端到端测试完整功能
- **性能测试（Performance Tests）**：测量速度与资源占用

### 2. 测试结构（AAA 模式）

- **Arrange（准备）**：准备测试数据与前置条件
- **Act（执行）**：执行被测代码
- **Assert（断言）**：验证结果

### 3. 测试覆盖率

- 测量测试覆盖了哪些代码
- 识别未被测试的代码路径
- 追求有意义的覆盖率，而不只是高百分比

### 4. 测试隔离

- 测试之间应当相互独立
- 测试之间不共享状态
- 每个测试都应自行清理

## 快速开始

```python
# test_example.py
def add(a, b):
    return a + b

def test_add():
    """Basic test example."""
    result = add(2, 3)
    assert result == 5

def test_add_negative():
    """Test with negative numbers."""
    assert add(-1, 1) == 0

# Run with: pytest test_example.py
```

## 详细模式与完整示例

详细的模式文档位于 `references/details.md`。当上方的导航层级不够用时，请阅读该文件。

## 测试最佳实践

### 测试组织

```python
# tests/
#   __init__.py
#   conftest.py           # Shared fixtures
#   test_unit/            # Unit tests
#     test_models.py
#     test_utils.py
#   test_integration/     # Integration tests
#     test_api.py
#     test_database.py
#   test_e2e/            # End-to-end tests
#     test_workflows.py
```

### 测试命名约定

一种常见模式：`test_<unit>_<scenario>_<expected_outcome>`。可按你团队的偏好调整。

```python
# Pattern: test_<unit>_<scenario>_<expected>
def test_create_user_with_valid_data_returns_user():
    ...

def test_create_user_with_duplicate_email_raises_conflict():
    ...

def test_get_user_with_unknown_id_returns_none():
    ...

# Good test names - clear and descriptive
def test_user_creation_with_valid_data():
    """Clear name describes what is being tested."""
    pass

def test_login_fails_with_invalid_password():
    """Name describes expected behavior."""
    pass

def test_api_returns_404_for_missing_resource():
    """Specific about inputs and expected outcomes."""
    pass

# Bad test names - avoid these
def test_1():  # Not descriptive
    pass

def test_user():  # Too vague
    pass

def test_function():  # Doesn't explain what's tested
    pass
```

### 测试重试行为

使用 mock 副作用（side effect）验证重试逻辑是否正确工作。

```python
from unittest.mock import Mock

def test_retries_on_transient_error():
    """Test that service retries on transient failures."""
    client = Mock()
    # Fail twice, then succeed
    client.request.side_effect = [
        ConnectionError("Failed"),
        ConnectionError("Failed"),
        {"status": "ok"},
    ]

    service = ServiceWithRetry(client, max_retries=3)
    result = service.fetch()

    assert result == {"status": "ok"}
    assert client.request.call_count == 3

def test_gives_up_after_max_retries():
    """Test that service stops retrying after max attempts."""
    client = Mock()
    client.request.side_effect = ConnectionError("Failed")

    service = ServiceWithRetry(client, max_retries=3)

    with pytest.raises(ConnectionError):
        service.fetch()

    assert client.request.call_count == 3

def test_does_not_retry_on_permanent_error():
    """Test that permanent errors are not retried."""
    client = Mock()
    client.request.side_effect = ValueError("Invalid input")

    service = ServiceWithRetry(client, max_retries=3)

    with pytest.raises(ValueError):
        service.fetch()

    # Only called once - no retry for ValueError
    assert client.request.call_count == 1
```

### 使用 Freezegun 对时间做 mock

使用 freezegun 在测试中控制时间，以获得可预测的依赖时间的行为。

```python
from freezegun import freeze_time
from datetime import datetime, timedelta

@freeze_time("2026-01-15 10:00:00")
def test_token_expiry():
    """Test token expires at correct time."""
    token = create_token(expires_in_seconds=3600)
    assert token.expires_at == datetime(2026, 1, 15, 11, 0, 0)

@freeze_time("2026-01-15 10:00:00")
def test_is_expired_returns_false_before_expiry():
    """Test token is not expired when within validity period."""
    token = create_token(expires_in_seconds=3600)
    assert not token.is_expired()

@freeze_time("2026-01-15 12:00:00")
def test_is_expired_returns_true_after_expiry():
    """Test token is expired after validity period."""
    token = Token(expires_at=datetime(2026, 1, 15, 11, 30, 0))
    assert token.is_expired()

def test_with_time_travel():
    """Test behavior across time using freeze_time context."""
    with freeze_time("2026-01-01") as frozen_time:
        item = create_item()
        assert item.created_at == datetime(2026, 1, 1)

        # Move forward in time
        frozen_time.move_to("2026-01-15")
        assert item.age_days == 14
```

### 测试标记

```python
# test_markers.py
import pytest

@pytest.mark.slow
def test_slow_operation():
    """Mark slow tests."""
    import time
    time.sleep(2)


@pytest.mark.integration
def test_database_integration():
    """Mark integration tests."""
    pass


@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    """Skip tests temporarily."""
    pass


@pytest.mark.skipif(os.name == "nt", reason="Unix only test")
def test_unix_specific():
    """Conditional skip."""
    pass


@pytest.mark.xfail(reason="Known bug #123")
def test_known_bug():
    """Mark expected failures."""
    assert False


# Run with:
# pytest -m slow          # Run only slow tests
# pytest -m "not slow"    # Skip slow tests
# pytest -m integration   # Run integration tests
```

### 覆盖率报告

```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=myapp tests/

# Generate HTML report
pytest --cov=myapp --cov-report=html tests/

# Fail if coverage below threshold
pytest --cov=myapp --cov-fail-under=80 tests/

# Show missing lines
pytest --cov=myapp --cov-report=term-missing tests/
```

关于进阶模式（异步测试、monkeypatching、基于属性的测试、数据库测试、CI/CD 集成以及配置），参见 [references/advanced-patterns.md](references/advanced-patterns.md)
