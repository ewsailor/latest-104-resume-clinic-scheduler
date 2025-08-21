# 文檔導覽

歡迎來到 104 履歷診療室專案文檔中心！這裡包含了專案的所有技術文檔、使用指南和最佳實踐。

## 📁 文檔結構

```
docs/
├── guides/                      # 使用指南
│   ├── setup/                   # 安裝和設定指南
│   ├── development/             # 開發指南
│   └── deployment/              # 部署指南
├── technical/                   # 技術文檔
│   ├── database/                # 資料庫相關
│   ├── api/                     # API 相關
│   └── architecture/            # 架構文檔
├── troubleshooting/             # 故障排除
├── examples/                    # 範例程式碼
├── best-practices/              # 最佳實踐
└── README.md                    # 本文件
```

## 🚀 快速開始

### 新手上路

1. **[安裝指南](guides/setup/installation.md)** - 專案安裝和環境設定
2. **[配置指南](guides/setup/configuration.md)** - 應用程式配置說明
3. **[資料庫設定](guides/setup/database-setup.md)** - 資料庫初始化和配置

### 開發指南

1. **[程式碼標準](guides/development/coding-standards.md)** - 程式碼風格和規範
2. **[測試指南](guides/development/testing-guide.md)** - 測試策略和執行方法
3. **[除錯指南](guides/development/debugging.md)** - 常見問題和除錯技巧

## 🔧 技術文檔

### 資料庫相關

- **[Alembic 遷移指南](technical/database/alembic_guide.md)** - 資料庫遷移管理
- **[連線最佳實踐](technical/database/database_connection_best_practices.md)** - 資料庫連線配置
- **[資料庫設計](technical/database/schema-design.md)** - 資料庫結構設計

### API 相關

- **[API 設計原則](technical/api/api-design.md)** - API 設計和實作原則
- **[端點文檔](technical/api/endpoints.md)** - API 端點詳細說明

### 架構文檔

- **[系統概覽](technical/architecture/system-overview.md)** - 系統架構和元件說明
- **[元件圖](technical/architecture/component-diagram.md)** - 系統元件關係圖

## 🛠️ 故障排除

### 常見問題

- **[時區解決方案](troubleshooting/timezone_solution.md)** - 時區相關問題解決
- **[Multipart 遷移](troubleshooting/python_multipart_migration.md)** - Multipart 模組遷移
- **[Multipart 使用](troubleshooting/python_multipart_usage.md)** - Multipart 模組使用說明

## 💡 最佳實踐

### 開發最佳實踐

- **[匯入指南](best-practices/import_guidelines.md)** - Python 模組匯入規範
- **[Import 自動修復](technical/utils/import-fix-guide.md)** - 函式內部 import 語句自動修復
- **[訊息優化](best-practices/message_optimization.md)** - 訊息處理優化技巧
- **[測試常數指南](best-practices/test_constants_guide.md)** - 測試常數管理
- **[測試常數重構](best-practices/test_constants_restructure.md)** - 測試常數重構說明

## 📝 範例程式碼

### 程式碼範例

- **[to_dict 方法範例](examples/to_dict_method_examples.py)** - to_dict 方法實作範例
- **[程式碼片段](examples/code-snippets.md)** - 常用程式碼片段

## 🎯 文檔貢獻

### 撰寫新文檔

1. 根據文檔類型選擇適當的目錄
2. 使用一致的命名規範
3. 遵循 Markdown 格式標準
4. 添加適當的目錄和連結

### 文檔標準

- **標題格式**: 使用 `#` 到 `######` 的層級標題
- **程式碼區塊**: 使用 ``` 包圍程式碼
- **連結格式**: 使用相對路徑連結到其他文檔
- **圖片**: 將圖片放在 `assets/` 目錄下

### 命名規範

- **檔案命名**: 使用小寫字母和連字號，如 `api-design.md`
- **目錄命名**: 使用描述性名稱，如 `database/`, `api/`
- **標題命名**: 使用繁體中文，清楚描述內容

## 📚 相關連結

- **[專案 README](../README.md)** - 專案概覽和快速開始
- **[測試指南](../tests/README.md)** - 測試策略和最佳實踐
- **[靜態檔案指南](../static/README.md)** - 靜態資源管理
- **[開發腳本說明](../scripts/README.md)** - 開發工具使用指南

## 🤝 貢獻指南

如果您發現文檔有錯誤或需要改進，請：

1. 開啟 Issue 描述問題
2. 提交 Pull Request 修正文檔
3. 確保文檔格式正確且內容準確
4. 更新相關的目錄和連結

---

**最後更新**: 2025-01-XX  
**維護者**: Oscar Chung
