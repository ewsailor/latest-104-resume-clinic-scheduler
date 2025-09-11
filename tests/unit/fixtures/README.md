# 單元測試 Fixtures

本目錄包含單元測試專用的 fixtures 和測試資料。

## 目錄結構

```
tests/unit/fixtures/
├── __init__.py          # 模組初始化
├── database.py          # 資料庫相關 fixtures
└── README.md           # 本文件
```

## Fixtures 說明

### 資料庫 Fixtures

#### `db_session`

- **用途**: 提供測試用的資料庫會話
- **類型**: `Session`
- **特點**:
  - 使用記憶體 SQLite 資料庫
  - 自動建立和清理資料表
  - 測試結束後自動關閉會話

**使用範例**:

```python
def test_create_schedule(db_session: Session):
    """測試建立時段功能。"""
    # 使用 db_session 進行資料庫操作
    schedule = create_schedule(db_session, schedule_data)
    assert schedule.id is not None
```

## 與 conftest.py 的關係

- **`conftest.py`**: 導入並重新導出 fixtures，確保 Pytest 能正確識別
- **`fixtures/`**: 實際的 fixtures 實作和組織

## 最佳實踐

1. **按功能分類**: 將相關的 fixtures 放在同一個文件中
2. **清晰的命名**: 使用描述性的 fixture 名稱
3. **適當的文檔**: 為每個 fixture 提供詳細的說明
4. **資源清理**: 確保 fixtures 正確清理資源

## 擴展指南

當需要添加新的 fixtures 時：

1. 創建新的文件（如 `models.py`、`services.py`）
2. 在 `conftest.py` 中導入新的 fixtures
3. 更新本 README 文檔
