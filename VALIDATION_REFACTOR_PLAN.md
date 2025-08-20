# 驗證與錯誤處理重構計劃

## 🎯 目標架構

### 1. **核心驗證層** (`app/validation/`)

```
app/validation/
├── __init__.py
├── base.py          # 基礎驗證器和介面
├── types.py         # 型別驗證器（int, string, date 等）
├── business.py      # 業務邏輯驗證器
└── decorators.py    # 驗證裝飾器
```

### 2. **錯誤處理層** (`app/errors/`)

```
app/errors/
├── __init__.py
├── exceptions.py    # 錯誤類型定義
├── codes.py         # 錯誤代碼常數
├── handlers.py      # 錯誤處理函式
└── formatters.py    # 錯誤格式化
```

### 3. **工具層** (`app/utils/`)

```
app/utils/
├── decorators.py    # 通用裝飾器（日誌、緩存等）
└── ... (其他工具)
```

## 📋 重構步驟

### Phase 1: 建立新的驗證架構

1. 創建 `app/validation/` 目錄
2. 實作基礎驗證器介面
3. 遷移型別驗證邏輯
4. 實作業務邏輯驗證器

### Phase 2: 重構錯誤處理

1. 創建 `app/errors/` 目錄
2. 分離錯誤類型和處理邏輯
3. 統一錯誤格式化

### Phase 3: 更新現有程式碼

1. 更新 CRUD 層使用新的驗證器
2. 更新路由層錯誤處理
3. 移除舊的模組

### Phase 4: 測試和驗證

1. 確保所有測試通過
2. 檢查效能影響
3. 更新文件

## 🔧 具體實作範例

### 基礎驗證器介面

```python
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

T = TypeVar('T')

class BaseValidator(ABC, Generic[T]):
    @abstractmethod
    def validate(self, value: Any) -> T:
        pass

    @abstractmethod
    def get_error_message(self, value: Any) -> str:
        pass
```

### 型別驗證器

```python
class PositiveIntValidator(BaseValidator[int]):
    def validate(self, value: Any) -> int:
        if not isinstance(value, int) or value <= 0:
            raise ValidationError(self.get_error_message(value))
        return value

    def get_error_message(self, value: Any) -> str:
        return f"必須為正整數，但得到: {value}"
```

### 業務邏輯驗證器

```python
class ScheduleValidator:
    def __init__(self):
        self.positive_int = PositiveIntValidator()
        self.date_validator = DateValidator()
        # ...

    def validate_schedule_data(self, data: ScheduleData) -> None:
        self.positive_int.validate(data.giver_id)
        self.date_validator.validate(data.schedule_date)
        self._validate_business_rules(data)
```

## ✅ 優點

1. **職責清晰**：每個模組只負責一件事
2. **易於測試**：驗證邏輯獨立，容易單元測試
3. **可重用性**：驗證器可在不同地方重用
4. **可擴展性**：新增驗證規則很容易
5. **一致性**：統一的錯誤處理方式
6. **維護性**：邏輯分離，修改影響範圍小

## 🔄 最新更新

### 營業時間驗證器改進 (2024-01-XX)

- **變更**：將營業時間從固定 09:00-22:00 改為排除休息時間 00:00-08:00
- **優點**：
  - 更符合實際使用場景（排除多數人的休息時間）
  - 支援跨越午夜的休息時間設定
  - 可自定義休息時間範圍
- **實作**：
  - 修改 `BusinessHoursValidator` 邏輯
  - 支援跨越午夜的休息時間（如 22:00-06:00）
  - 更新預設參數和錯誤訊息

## 🎭 設計模式

- **Strategy Pattern**: 不同的驗證策略
- **Decorator Pattern**: 驗證裝飾器
- **Factory Pattern**: 驗證器工廠
- **Chain of Responsibility**: 驗證鏈
