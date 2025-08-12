-- ===== 更新使用者 email 地址為統一格式 =====
-- 將所有使用者的 email 更新為 wang01@example.com 到 wang14@example.com
-- 建立日期：2025-01-16
-- 執行前請先備份資料！

USE scheduler_db;

-- 設定時區
SET time_zone = '+08:00';

-- 顯示更新前的資料
SELECT '=== 更新前的使用者資料 ===' AS info;
SELECT id, name, email, updated_at
FROM users 
WHERE deleted_at IS NULL 
ORDER BY id;

-- 開始交易
START TRANSACTION;

-- 更新 email 地址
UPDATE users SET 
    email = CASE id
        WHEN 1 THEN 'wang01@example.com'
        WHEN 2 THEN 'wang02@example.com'
        WHEN 3 THEN 'wang03@example.com'
        WHEN 4 THEN 'wang04@example.com'
        WHEN 5 THEN 'wang05@example.com'
        WHEN 6 THEN 'wang06@example.com'
        WHEN 7 THEN 'wang07@example.com'
        WHEN 8 THEN 'wang08@example.com'
        WHEN 9 THEN 'wang09@example.com'
        WHEN 10 THEN 'wang10@example.com'
        WHEN 11 THEN 'wang11@example.com'
        WHEN 12 THEN 'wang12@example.com'
        WHEN 13 THEN 'wang13@example.com'
        WHEN 14 THEN 'wang14@example.com'
        ELSE email  -- 保持原有 email（如果有其他 ID）
    END,
    updated_at = NOW()
WHERE id BETWEEN 1 AND 14 
  AND deleted_at IS NULL;

-- 顯示更新的筆數
SELECT CONCAT('已更新 ', ROW_COUNT(), ' 筆記錄') AS update_result;

-- 顯示更新後的資料
SELECT '=== 更新後的使用者資料 ===' AS info;
SELECT id, name, email, updated_at
FROM users 
WHERE deleted_at IS NULL 
ORDER BY id;

-- 驗證 email 格式是否正確
SELECT '=== 驗證 email 格式 ===' AS info;
SELECT 
    id,
    name,
    email,
    CASE 
        WHEN email REGEXP '^wang[0-9]{2}@example\.com$' THEN '✅ 格式正確'
        ELSE '❌ 格式錯誤'
    END AS email_format_check
FROM users 
WHERE deleted_at IS NULL 
ORDER BY id;

-- 如果一切正常，請手動執行 COMMIT;
-- 如果有問題，請執行 ROLLBACK;

-- 提示訊息
SELECT '請檢查上述結果，確認無誤後執行 COMMIT; 提交變更，或執行 ROLLBACK; 回滾變更' AS reminder;
