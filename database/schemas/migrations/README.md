# 資料庫遷移說明

## 遷移歷史

### v1 → v2 (Corrected)
- 修正了資料庫結構中的錯誤
- 更新了欄位型別和約束

### v2 → v3 (UTC)
- 將時區設定改為 UTC
- 統一時間戳記格式

### v3 → v4 (Best Practice)
- 套用資料庫最佳實踐
- 優化索引和約束

## 遷移步驟

### 1. 建立備份
```bash
# 建立完整備份
mysqldump -u username -p database_name > backup_before_migration_YYYYMMDD_HHMMSS.sql
```

### 2. 執行遷移
```bash
# 執行遷移腳本
mysql -u username -p database_name < migration_script.sql
```

### 3. 驗證遷移
```bash
# 檢查資料庫結構
mysql -u username -p -e "DESCRIBE table_name;" database_name
```

## 注意事項
- 遷移前務必建立完整備份
- 在測試環境中先執行遷移
- 記錄所有遷移步驟和結果
- 遷移後進行功能測試
