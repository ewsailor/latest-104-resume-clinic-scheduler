# 裝飾器模組

本模組提供各種實用的裝飾器，用於簡化程式碼並提供統一的錯誤處理、日誌記錄等功能。

## 目錄結構

```
app/utils/decorators/
├── __init__.py              # 模組初始化，重新導出所有裝飾器
├── crud_decorators.py       # CRUD 操作相關裝飾器
├── logging_decorators.py    # 日誌記錄相關裝飾器
└── README.md               # 本文件
```

## 可用的裝飾器

### CRUD 裝飾器 (`crud_decorators.py`)

#### `handle_crud_errors(error_context: str)`

統一的 CRUD 錯誤處理裝飾器。

```python
from app.utils.decorators import handle_crud_errors

@handle_crud_errors("建立使用者")
def create_user(self, db: Session, user_data: dict):
    # 您的 CRUD 邏輯
    pass
```

#### `handle_crud_errors_with_rollback(error_context: str)`

帶資料庫回滾功能的錯誤處理裝飾器。

```python
from app.utils.decorators import handle_crud_errors_with_rollback

@handle_crud_errors_with_rollback("更新使用者")
def update_user(self, db: Session, user_id: int, user_data: dict):
    # 您的 CRUD 邏輯
    pass
```

#### `log_operation(operation_name: str)`

CRUD 操作日誌記錄裝飾器。

```python
from app.utils.decorators import log_operation

@log_operation("查詢使用者")
def get_user(self, db: Session, user_id: int):
    # 您的查詢邏輯
    pass
```

### 日誌裝飾器 (`logging_decorators.py`)

#### `log_execution_time(func_name: str = None)`

記錄函式執行時間的裝飾器。

```python
from app.utils.decorators import log_execution_time

@log_execution_time("資料處理")
def process_data(self, data: list):
    # 您的資料處理邏輯
    pass
```

#### `log_function_parameters(log_args: bool = True, log_kwargs: bool = True)`

記錄函式參數的裝飾器。

```python
from app.utils.decorators import log_function_parameters

@log_function_parameters(log_args=True, log_kwargs=False)
def complex_calculation(self, x: int, y: int, *, precision: int = 2):
    # 您的計算邏輯
    pass
```

#### `retry_on_exception(max_retries: int = 3, delay: float = 1.0)`

異常重試裝飾器。

```python
from app.utils.decorators import retry_on_exception

@retry_on_exception(max_retries=5, delay=2.0)
def call_external_api(self, url: str):
    # 您的 API 調用邏輯
    pass
```

## 使用範例

### 組合使用多個裝飾器

```python
from app.utils.decorators import (
    handle_crud_errors_with_rollback,
    log_execution_time,
    log_function_parameters
)

class UserService:
    @handle_crud_errors_with_rollback("建立使用者")
    @log_execution_time("使用者建立")
    @log_function_parameters(log_args=False, log_kwargs=True)
    def create_user(self, db: Session, *, name: str, email: str):
        # 建立使用者的邏輯
        pass
```

### 自定義錯誤處理

```python
from app.utils.decorators import handle_crud_errors

@handle_crud_errors("驗證使用者資料")
def validate_user_data(self, user_data: dict):
    if not user_data.get('email'):
        raise ValueError("電子信箱是必填欄位")

    if not user_data.get('name'):
        raise ValueError("姓名是必填欄位")

    return True
```

## 添加新的裝飾器

要添加新的裝飾器，請遵循以下步驟：

1. **創建新的裝飾器檔案**：

   ```python
   # app/utils/decorators/new_decorators.py

   import functools
   from typing import Any, Callable

   def my_new_decorator(param: str):
       def decorator(func: Callable) -> Callable:
           @functools.wraps(func)
           def wrapper(*args, **kwargs) -> Any:
               # 您的裝飾器邏輯
               return func(*args, **kwargs)
           return wrapper
       return decorator
   ```

2. **更新 `__init__.py`**：

   ```python
   # app/utils/decorators/__init__.py

   from .new_decorators import my_new_decorator

   __all__ = [
       # ... 現有的裝飾器
       "my_new_decorator",
   ]
   ```

3. **更新 `app/utils/__init__.py`**：

   ```python
   # app/utils/__init__.py

   from .decorators import my_new_decorator

   __all__ = [
       # ... 現有的項目
       "my_new_decorator",
   ]
   ```

## 最佳實踐

1. **保持裝飾器簡單**：每個裝飾器應該只負責一個特定功能
2. **使用 `functools.wraps`**：保持原函式的元資料
3. **提供清晰的錯誤訊息**：幫助除錯
4. **記錄適當的日誌**：便於監控和除錯
5. **考慮效能影響**：避免在裝飾器中執行昂貴的操作

## 測試

所有裝飾器都有對應的測試檔案：

```
tests/unit/utils/decorators/
├── test_crud_decorators.py
└── test_logging_decorators.py  # 待創建
```

## 相關連結

- [Python 裝飾器官方文件](https://docs.python.org/3/glossary.html#term-decorator)
- [functools.wraps 文件](https://docs.python.org/3/library/functools.html#functools.wraps)
