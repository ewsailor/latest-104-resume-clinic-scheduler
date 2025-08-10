-- ===== 使用者資料表 `users` ===== 
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (         
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY 
        COMMENT '使用者 ID',
    `name` VARCHAR(100) NOT NULL 
        COMMENT '使用者姓名', 
    `email` VARCHAR(191) NOT NULL UNIQUE 
        COMMENT '電子信箱（唯一）',    
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP 
        COMMENT '建立時間 (本地時間)',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP 
        COMMENT '更新時間 (本地時間)',
    `deleted_at` DATETIME NULL DEFAULT NULL 
        COMMENT '軟刪除標記 (本地時間)',
    `updated_by` INT UNSIGNED NULL 
        COMMENT '最後更新者的使用者 ID，可為 NULL（表示系統自動更新）',
    
    -- 外鍵約束
    CONSTRAINT `fk_users_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
    
-- 指定儲存引擎、預設字符集、排序規則
) ENGINE = InnoDB 
    DEFAULT CHARSET = utf8mb4 
    COLLATE = utf8mb4_unicode_ci 
    COMMENT = '使用者資料表 (本地時間戳記)';

-- 使用者資料表索引（加速查詢）
CREATE INDEX `idx_email`
    ON `users` (`email`);
CREATE INDEX `idx_deleted_at` 
    ON `users` (`deleted_at`);
CREATE INDEX `fk_users_updated_by` 
    ON `users` (`updated_by`);
