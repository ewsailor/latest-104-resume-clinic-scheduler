## 📋 測試最佳實踐

### 1. 測試結構

```python
def test_function_name():
    """測試描述"""
    # Arrange (準備)
    input_data = "test_data"

    # Act (執行)
    result = function_to_test(input_data)

    # Assert (驗證)
    assert result == expected_output
```

### 2. 使用 Fixtures

```python
@pytest.fixture
def sample_user():
    """提供測試用的使用者資料"""
    return User(
        name="測試使用者",
        email="test@example.com"
    )

def test_create_user(sample_user):
    """測試建立使用者"""
    # 使用 fixture 提供的資料
    assert sample_user.name == "測試使用者"
```

### 3. 使用 Mock

```python
def test_external_api_call(mocker):
    """測試外部 API 呼叫"""
    # Mock 外部 API
    mock_api = mocker.patch('app.utils.external_api.call')
    mock_api.return_value = {"status": "success"}

    # 執行測試
    result = function_that_calls_api()

    # 驗證結果
    assert result["status"] == "success"
    mock_api.assert_called_once()
```

### 4. 資料庫測試

```python
def test_create_schedule(db_session):
    """測試建立排程"""
    # 準備測試資料
    schedule_data = ScheduleData(
        giver_id=1,
        schedule_date=date(2024, 1, 1),
        start_time=time(9, 0),
        end_time=time(10, 0)
    )

    # 執行測試
    schedule = schedule_crud.create_schedule(db_session, schedule_data)

    # 驗證結果
    assert schedule.giver_id == 1
    assert schedule.schedule_date == date(2024, 1, 1)
```

## 🎯 測試覆蓋率目標

- **單元測試**: 90% 以上
- **整合測試**: 80% 以上
- **端到端測試**: 關鍵流程 100%

## 📝 維護指南

### 新增測試

1. 根據測試類型選擇適當的目錄
2. 使用一致的命名規範
3. 撰寫清晰的測試描述
4. 確保測試的可重複性

### 更新測試

1. 當功能變更時，同步更新相關測試
2. 保持測試資料的一致性
3. 定期清理過時的測試

### 測試資料管理

1. 使用 conftest.py 提供共享的 fixtures
2. 避免硬編碼測試資料
3. 確保測試資料的隔離性
