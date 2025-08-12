# Python 匯入指南

## 🎯 匯入最佳實踐

### 基本原則

1. **包內使用相對匯入**
2. **包外使用絕對匯入**
3. **避免循環匯入**
4. **保持模組獨立性**

## 📁 專案結構

```
app/
├── __init__.py
├── core/
│   ├── __init__.py          # 使用相對匯入
│   └── settings.py
├── routers/
│   ├── __init__.py          # 使用相對匯入
│   └── main.py
└── main.py                  # 使用絕對匯入
```

## 🔧 匯入範例

### 包內匯入（相對匯入）

```python
# app/core/__init__.py
from .settings import Settings, settings, get_project_version

# app/routers/__init__.py
from .main import router

# app/models/__init__.py
from .database import Database
```

### 包外匯入（絕對匯入）

```python
# app/main.py
from app.core import settings, get_project_version
from app.routers import router
from app.models import Database

# scripts/config_validator.py
from app.core import settings

# tests/test_config.py
from app.core import Settings
```

## ✅ 正確的匯入方式

### 1. 核心模組匯入

```python
# ✅ 正確：外部模組匯入
from app.core import settings, get_project_version

# ✅ 正確：內部模組匯入
from .settings import Settings, settings, get_project_version
```

### 2. 路由模組匯入

```python
# ✅ 正確：外部模組匯入
from app.routers.main import router

# ✅ 正確：內部模組匯入
from .main import router
```

### 3. 模型模組匯入

```python
# ✅ 正確：外部模組匯入
from app.models.database import Database

# ✅ 正確：內部模組匯入
from .database import Database
```

## ❌ 避免的匯入方式

### 1. 絕對匯入在包內

```python
# ❌ 錯誤：包內使用絕對匯入
# app/core/__init__.py
from app.core.settings import Settings, settings, get_project_version
```

### 2. 過度具體的匯入

```python
# ❌ 錯誤：過度具體
from app.core.settings import Settings
from app.core.settings import settings
from app.core.settings import get_project_version

# ✅ 正確：合併匯入
from app.core import Settings, settings, get_project_version
```

### 3. 循環匯入

```python
# ❌ 錯誤：可能造成循環匯入
# app/core/__init__.py
from app.routers import router  # 如果 routers 也匯入 core

# ✅ 正確：使用依賴注入
# 在需要時才匯入，或使用 lazy loading
```

## 🎯 最佳實踐要點

### 1. 匯入順序

```python
# 標準函式庫
import os
import sys
from pathlib import Path

# 第三方套件
from fastapi import FastAPI
from pydantic import BaseSettings

# 本地模組（絕對匯入）
from app.core import settings
from app.routers import router

# 本地模組（相對匯入，僅在包內）
from .settings import Settings
```

### 2. 匯入別名

```python
# 避免名稱衝突
from app.routers.main import router as main_router
from app.routers.schedule import router as schedule_router

# 簡化長名稱
from app.core.settings import Settings as AppSettings
```

### 3. 條件匯入

```python
# 避免循環匯入
try:
    from .database import Database
except ImportError:
    Database = None

# 或使用 TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .database import Database
```

## 🔍 常見問題

### Q: 為什麼包內要使用相對匯入？

A:

- **模組獨立性**：不依賴專案結構
- **重構友好**：移動模組時無需修改
- **避免循環匯入**：減少依賴複雜度
- **Python 慣例**：符合 PEP 8 建議

### Q: 什麼時候使用絕對匯入？

A:

- **包外模組**：從其他包匯入
- **腳本檔案**：獨立的執行腳本
- **測試檔案**：測試模組功能
- **文檔範例**：展示使用方式

### Q: 如何避免循環匯入？

A:

- **依賴注入**：在需要時才匯入
- **延遲匯入**：使用 lazy loading
- **重構設計**：重新組織模組結構
- **使用 TYPE_CHECKING**：僅在型別檢查時匯入

## 📊 匯入檢查清單

- [ ] 包內使用相對匯入
- [ ] 包外使用絕對匯入
- [ ] 避免循環匯入
- [ ] 匯入順序正確
- [ ] 使用適當的別名
- [ ] 避免過度具體的匯入
- [ ] 文檔化匯入方式
