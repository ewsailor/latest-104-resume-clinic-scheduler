-- ===== 【MVP】104 履歷診療室 - 站內諮詢時間媒合系統 - 資料庫結構 (本地時間版本) =====
-- 建立日期：2025-08-06
-- 版本：2.1.0
-- 描述：使用本地時間戳記的完整資料庫結構，包含軟刪除、來源追蹤等最佳實踐


-- ===== 資料庫 =====
-- 檢查資料庫是否存在：顯示目前 MySQL 伺服器上所有的資料庫名稱
SHOW DATABASES;

-- 刪除並重新創建資料庫，加上字符集和排序規則，然後切換到 scheduler_db 資料庫
DROP DATABASE IF EXISTS `scheduler_db`;
CREATE DATABASE `scheduler_db` 
    DEFAULT CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;
USE `scheduler_db`; 


-- ===== 資料庫使用者 =====
-- 先刪除舊的，確保乾淨狀態（如果使用者已存在）
DROP USER IF EXISTS 'fastapi_user'@'localhost';

-- 重建使用者：新增名為 fastapi_user 的使用者，密碼為 fastapi123
CREATE USER 'fastapi_user'@'localhost' 
    IDENTIFIED BY 'fastapi123';


-- ===== 資料庫權限 =====
-- 撤銷任何意外預設權限（通常 DROP USER 後不需要，但加上更保險）
REVOKE ALL PRIVILEGES ON `scheduler_db`.* 
    FROM 'fastapi_user'@'localhost'; 

-- 授予權限：給予 fastapi_user 在 scheduler_db 這個資料庫上所有資料表，必要的權限
-- （而不是用 GRANT ALL PRIVILEGES，給所有資料表的全部權限）
-- 包含基本的 CRUD 操作和結構管理權限，不包含 DROP、GRANT 等管理權限，確保安全性
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, ALTER 
    ON `scheduler_db`.* 
    TO 'fastapi_user'@'localhost';

-- 重新整理權限表，讓權限即時生效
FLUSH PRIVILEGES;

-- 檢查資料庫使用者權限：顯示 fastapi_user 的所有授權清單，確認是否設置成功
SHOW GRANTS FOR 'fastapi_user'@'localhost';


-- ===== 使用者資料表 `users` ===== 
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (         
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY 
        COMMENT '使用者 ID',
    `name` VARCHAR(100) NOT NULL 
        COMMENT '使用者姓名', 
    `email` VARCHAR(191) NOT NULL UNIQUE 
        COMMENT '電子信箱（唯一）',    
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL 
        COMMENT '建立時間（本地時間）',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL 
        COMMENT '更新時間（本地時間）',
    `updated_by` INT UNSIGNED NULL 
        COMMENT '最後更新的使用者 ID，可為 NULL（表示系統自動更新）',
    `deleted_at` DATETIME NULL DEFAULT NULL 
        COMMENT '軟刪除標記（本地時間）',
    
    -- 自我關聯外鍵約束
    CONSTRAINT `fk_users_updated_by` 
        FOREIGN KEY (`updated_by`) 
        REFERENCES `users` (`id`) 
        ON DELETE SET NULL      -- 靈活：使用者刪除時設為 NULL
        ON UPDATE CASCADE,      -- 更新：如果使用者 ID 改變，自動同步

-- 指定儲存引擎、預設字符集、排序規則
) ENGINE = InnoDB 
    DEFAULT CHARSET = utf8mb4 
    COLLATE = utf8mb4_unicode_ci 
    COMMENT = '使用者資料表 (本地時間戳記)';

-- 使用者資料表索引（加速查詢）
CREATE INDEX `idx_deleted_at` 
    ON `users` (`deleted_at`);

-- ===== 諮詢時段資料表 `schedules` ===== 
DROP TABLE IF EXISTS `schedules`;
CREATE TABLE `schedules` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY 
        COMMENT '諮詢時段 ID',
    `giver_id` INT UNSIGNED NOT NULL 
        COMMENT 'Giver 使用者 ID',
    `taker_id` INT UNSIGNED DEFAULT NULL 
        COMMENT 'Taker 使用者 ID，可為 NULL（表示 Giver 提供時段供 Taker 預約）', 
    `status` ENUM('DRAFT', 'AVAILABLE', 'PENDING', 'ACCEPTED', 'REJECTED', 'CANCELLED', 'COMPLETED') 
        NOT NULL DEFAULT 'DRAFT' 
        COMMENT '諮詢時段狀態',
    `date` DATE NOT NULL 
        COMMENT '日期 ',
    `start_time` TIME NOT NULL 
        COMMENT '開始時間',
    `end_time` TIME NOT NULL 
        COMMENT '結束時間',
    `note` VARCHAR(255) 
        COMMENT '備註，可為空',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL 
        COMMENT '建立時間（本地時間）',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL 
        COMMENT '更新時間（本地時間）',
    `updated_by` INT UNSIGNED NULL 
        COMMENT '最後更新的使用者 ID，可為 NULL（表示系統自動更新）',
    `updated_by_role` ENUM('GIVER', 'TAKER', 'SYSTEM') NULL 
        COMMENT '最後更新者角色',
    `deleted_at` DATETIME NULL DEFAULT NULL 
        COMMENT '軟刪除標記（本地時間）',
    
    -- ===== 外鍵約束 =====
    CONSTRAINT `fk_schedules_giver` 
        FOREIGN KEY (`giver_id`) 
        REFERENCES `users`(`id`)
        ON DELETE RESTRICT      -- 保護：不能刪除有時段的 Giver
        ON UPDATE CASCADE,      -- 更新：如果 Giver ID 改變，自動同步
    CONSTRAINT `fk_schedules_taker` 
        FOREIGN KEY (`taker_id`) 
        REFERENCES `users`(`id`)
        ON DELETE SET NULL      -- 靈活：Taker 刪除時設為 NULL（時段變可預約）
        ON UPDATE CASCADE,      -- 更新：如果 Taker ID 改變，自動同步
    CONSTRAINT `fk_schedules_updated_by` 
        FOREIGN KEY (`updated_by`) 
        REFERENCES `users`(`id`)
        ON DELETE SET NULL      -- 稽核：更新者刪除時保留記錄但設為 NULL
        ON UPDATE CASCADE,      -- 更新：自動同步 ID 變更
    
    -- ===== 業務邏輯約束 =====
    CONSTRAINT `chk_schedules_time_order` 
        CHECK (`start_time` < `end_time`)
-- 指定儲存引擎、預設字符集、排序規則
) ENGINE = InnoDB 
    DEFAULT CHARSET = utf8mb4 
    COLLATE = utf8mb4_unicode_ci 
    COMMENT = '諮詢時段資料表 (本地時間戳記)';


-- ===== 加速查詢用的索引 =====

-- 日期範圍查詢（行事曆介面常見）
CREATE INDEX `idx_schedule_date`
    ON `schedules` (`date`);

-- 複合索引：Giver + 日期（Giver 查詢自己的時段，包含單欄位查詢）
CREATE INDEX `idx_schedule_giver_date` 
    ON `schedules` (`giver_id`, `date`);

-- 複合索引：Taker + 日期（Taker 查詢自己的預約，包含單欄位查詢）
CREATE INDEX `idx_schedule_taker_date` 
    ON `schedules` (`taker_id`, `date`);

-- 軟刪除查詢（基礎功能，幾乎所有查詢，都需要過濾已刪除記錄）
CREATE INDEX `idx_schedule_deleted_at` 
    ON `schedules` (`deleted_at`);

-- 可用時段查詢（支援 is_available 屬性，高頻使用）
CREATE INDEX `idx_schedule_available` 
    ON `schedules` (`deleted_at`, `status`, `taker_id`);


-- ===== 結構驗證 =====
SHOW TABLES;
DESCRIBE `users`;
DESCRIBE `schedules`;


-- ===== 快速查詢驗證資料 =====
SELECT * FROM `schedules` 
    ORDER BY `id` DESC;