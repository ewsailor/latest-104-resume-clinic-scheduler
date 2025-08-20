# 參數驗證工具使用指南

## 概述

參數驗證工具模組 (`app/utils/validators.py`) 提供統一的參數驗證功能，減少重複的驗證程式碼。本指南說明如何使用這些工具來優化你的 CRUD 操作。

## 問題背景

在 CRUD 操作中，經常會看到重複的參數驗證程式碼：

```python
# 重複的驗證模式
if not isinstance(user_id, int) or user_id <= 0:
    raise ValueError(f"無效的 user_id: {user_id}")

if not isinstance(context, str):
    raise ValueError(f"無效的 context 類型: {type(context).__name__}, 期望 str")

if start_time >= end_time:
    raise ValueError(f"開始時間必須早於結束時間: {start_time} >= {end_time}")
```

這種重複的驗證程式碼會：

- 增加程式碼量
- 降低可維護性
- 容易出錯
- 不一致的錯誤訊息格式

## 解決方案

### 1. 直接使用驗證器方法

```python
from app.utils.validators import validator

def create_user(db: Session, user_id: int, name: str, age: int | None = None):
    # 使用驗證器方法
    user_id = validator.validate_positive_int(user_id, "user_id")
    name = validator.validate_string(name, "name", min_length=1)
    age = validator.validate_optional_positive_int(age, "age")

    # 業務邏輯...
```

### 2. 使用裝飾器驗證

```python
from app.utils.validators import validate_parameters

@validate_parameters(
    user_id=dict(type=int, min_value=1),
    name=dict(type=str, min_length=1),
    age=dict(type=int, min_value=0, optional=True)
)
def create_user(db: Session, user_id: int, name: str, age: int | None = None):
    # 業務邏輯，無需手動驗證
    pass
```

## 可用的驗證方法

### 基本驗證方法

| 方法                               | 說明           | 範例                                                                  |
| ---------------------------------- | -------------- | --------------------------------------------------------------------- |
| `validate_required()`              | 驗證必需參數   | `validator.validate_required(value, "param_name", int, min_value=1)`  |
| `validate_optional()`              | 驗證可選參數   | `validator.validate_optional(value, "param_name", str)`               |
| `validate_positive_int()`          | 驗證正整數     | `validator.validate_positive_int(user_id, "user_id")`                 |
| `validate_optional_positive_int()` | 驗證可選正整數 | `validator.validate_optional_positive_int(age, "age")`                |
| `validate_string()`                | 驗證字串       | `validator.validate_string(name, "name", min_length=1)`               |
| `validate_optional_string()`       | 驗證可選字串   | `validator.validate_optional_string(description, "description")`      |
| `validate_list()`                  | 驗證列表       | `validator.validate_list(items, "items", str)`                        |
| `validate_optional_list()`         | 驗證可選列表   | `validator.validate_optional_list(tags, "tags", str)`                 |
| `validate_date()`                  | 驗證日期       | `validator.validate_date(schedule_date, "schedule_date")`             |
| `validate_time()`                  | 驗證時間       | `validator.validate_time(start_time, "start_time")`                   |
| `validate_time_range()`            | 驗證時間範圍   | `validator.validate_time_range(start_time, end_time)`                 |
| `validate_enum_value()`            | 驗證枚舉值     | `validator.validate_enum_value(status, "status", ScheduleStatusEnum)` |

### 裝飾器驗證規則

| 規則           | 說明             | 範例                                  |
| -------------- | ---------------- | ------------------------------------- |
| `type`         | 期望的型別       | `dict(type=int)`                      |
| `min_value`    | 最小值（數字）   | `dict(type=int, min_value=1)`         |
| `max_value`    | 最大值（數字）   | `dict(type=int, max_value=100)`       |
| `min_length`   | 最小長度（字串） | `dict(type=str, min_length=1)`        |
| `optional`     | 是否為可選參數   | `dict(type=str, optional=True)`       |
| `enum_class`   | 枚舉類別         | `dict(enum_class=ScheduleStatusEnum)` |
| `element_type` | 列表元素型別     | `dict(type=list, element_type=str)`   |

## 實際應用範例

### 1. 重構前的程式碼

```python
def check_schedule_overlap(self, db: Session, giver_id: int, schedule_date: date,
                          start_time: time, end_time: time, exclude_schedule_id: int | None = None):
    # 驗證輸入參數
    if not isinstance(giver_id, int) or giver_id <= 0:
        raise ValueError(f"無效的 giver_id: {giver_id}")

    if not isinstance(schedule_date, date):
        raise ValueError(f"無效的 schedule_date: {schedule_date}")

    if not isinstance(start_time, time):
        raise ValueError(f"無效的 start_time: {start_time}")

    if not isinstance(end_time, time):
        raise ValueError(f"無效的 end_time: {end_time}")

    if start_time >= end_time:
        raise ValueError(f"開始時間必須早於結束時間: {start_time} >= {end_time}")

    # 排除指定時段（用於更新時排除自己）
    if exclude_schedule_id is not None:
        if not isinstance(exclude_schedule_id, int) or exclude_schedule_id <= 0:
            raise ValueError(f"無效的 exclude_schedule_id: {exclude_schedule_id}")

    # 業務邏輯...
```

### 2. 重構後的程式碼

```python
def check_schedule_overlap(self, db: Session, giver_id: int, schedule_date: date,
                          start_time: time, end_time: time, exclude_schedule_id: int | None = None):
    # 使用新的驗證工具
    giver_id = validator.validate_positive_int(giver_id, "giver_id")
    schedule_date = validator.validate_date(schedule_date, "schedule_date")
    start_time = validator.validate_time(start_time, "start_time")
    end_time = validator.validate_time(end_time, "end_time")
    exclude_schedule_id = validator.validate_optional_positive_int(
        exclude_schedule_id, "exclude_schedule_id"
    )

    # 驗證時間範圍
    validator.validate_time_range(start_time, end_time)

    # 業務邏輯...
```

### 3. 使用裝飾器的版本

```python
@validate_parameters(
    giver_id=dict(type=int, min_value=1),
    schedule_date=dict(type=date),
    start_time=dict(type=time),
    end_time=dict(type=time),
    exclude_schedule_id=dict(type=int, min_value=1, optional=True)
)
def check_schedule_overlap(self, db: Session, giver_id: int, schedule_date: date,
                          start_time: time, end_time: time, exclude_schedule_id: int | None = None):
    # 驗證時間範圍（需要額外驗證）
    validator.validate_time_range(start_time, end_time)

    # 業務邏輯...
```

## 最佳實踐

### 1. 選擇合適的驗證方式

- **簡單驗證**：使用直接方法調用
- **複雜驗證**：使用裝飾器
- **跨參數驗證**：使用直接方法調用（如時間範圍驗證）

### 2. 錯誤處理

所有驗證方法都會拋出 `ValidationError`，這是一個統一的錯誤類型：

```python
from app.utils.error_handler import ValidationError

try:
    user_id = validator.validate_positive_int(user_id, "user_id")
except ValidationError as e:
    # 處理驗證錯誤
    logger.error(f"參數驗證失敗: {e}")
    raise
```

### 3. 與 CRUD 裝飾器結合使用

```python
@handle_crud_errors_with_rollback("建立時段")
@log_crud_operation("建立時段", log_args=False)
@validate_parameters(
    giver_id=dict(type=int, min_value=1),
    schedule_date=dict(type=date),
    start_time=dict(type=time),
    end_time=dict(type=time)
)
def create_schedule(self, db: Session, giver_id: int, schedule_date: date,
                   start_time: time, end_time: time):
    # 驗證時間範圍
    validator.validate_time_range(start_time, end_time)

    # 業務邏輯...
```

### 4. 自定義驗證

對於特殊的驗證需求，可以擴展現有的驗證器：

```python
class CustomValidator(ParameterValidator):
    @staticmethod
    def validate_email(value: Any, param_name: str) -> str:
        """驗證電子郵件格式"""
        result = CustomValidator.validate_string(value, param_name)

        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, result):
            raise ValidationError(f"無效的 {param_name} 格式: {result}")

        return result
```

## 遷移步驟

### 1. 識別重複的驗證程式碼

```bash
grep -r "if not isinstance" app/crud/
grep -r "raise ValueError" app/crud/
```

### 2. 逐步替換

1. 先替換簡單的型別驗證
2. 再替換數值範圍驗證
3. 最後替換複雜的業務邏輯驗證

### 3. 測試驗證

確保所有驗證邏輯正確工作：

```bash
python -m pytest tests/unit/utils/test_validators.py -v
```

## 優點

1. **減少重複程式碼**：統一的驗證邏輯
2. **提高可維護性**：集中管理驗證規則
3. **一致性**：統一的錯誤訊息格式
4. **可讀性**：清晰的驗證意圖
5. **可測試性**：獨立的驗證邏輯易於測試

## 注意事項

1. **性能影響**：裝飾器會增加少量執行開銷
2. **學習成本**：團隊需要學習新的驗證方式
3. **向後相容性**：確保現有程式碼不受影響

## 總結

參數驗證工具提供了一個優雅的解決方案來處理重複的參數驗證程式碼。通過使用這些工具，你可以：

- 大幅減少重複程式碼
- 提高程式碼的可維護性
- 確保驗證邏輯的一致性
- 讓程式碼更加清晰易讀

建議在專案中逐步採用這些工具，從最常用的驗證開始，逐步擴展到更複雜的場景。
