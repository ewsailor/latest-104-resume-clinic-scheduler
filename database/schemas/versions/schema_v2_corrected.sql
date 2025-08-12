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

-- ===== 修正版本：新增 created_by_role 欄位 =====

CREATE TABLE `schedules` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY 
        COMMENT '諮詢時段 ID',
    `giver_id` INT UNSIGNED NOT NULL 
        COMMENT 'Giver 使用者 ID',
    `taker_id` INT UNSIGNED DEFAULT NULL 
        COMMENT 'Taker 使用者 ID，可為 NULL', 
    `status` ENUM('DRAFT', 'AVAILABLE', 'PENDING', 'ACCEPTED', 'REJECTED', 'CANCELLED', 'COMPLETED') 
        NOT NULL DEFAULT 'DRAFT' 
        COMMENT '諮詢時段狀態',
    `date` DATE NOT NULL 
        COMMENT '日期 (yyyy-mm-dd)',
    `start_time` TIME NOT NULL 
        COMMENT '開始時間 (hh:mm)',
    `end_time` TIME NOT NULL 
        COMMENT '結束時間 (hh:mm)',
    `note` VARCHAR(255) 
        COMMENT '備註，可為空',
    
    -- ===== 建立者資訊 =====
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL 
        COMMENT '建立時間 (本地時間)',
    `created_by` INT UNSIGNED NULL 
        COMMENT '建立者的使用者 ID，可為 NULL',
    `created_by_role` ENUM('GIVER', 'TAKER', 'SYSTEM') NULL 
        COMMENT '建立者角色：GIVER、TAKER 或 SYSTEM',
    
    -- ===== 更新者資訊 =====
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL 
        COMMENT '更新時間 (本地時間)',
    `updated_by` INT UNSIGNED NULL 
        COMMENT '最後更新者的使用者 ID，可為 NULL',
    `updated_by_role` ENUM('GIVER', 'TAKER', 'SYSTEM') NULL 
        COMMENT '最後更新者角色：GIVER、TAKER 或 SYSTEM',
    
    `deleted_at` DATETIME NULL DEFAULT NULL 
        COMMENT '軟刪除標記 (本地時間)',
    
    -- ===== 外鍵約束 =====
    CONSTRAINT `fk_schedules_giver` 
        FOREIGN KEY (`giver_id`) 
        REFERENCES `users`(`id`)
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    CONSTRAINT `fk_schedules_taker` 
        FOREIGN KEY (`taker_id`) 
        REFERENCES `users`(`id`)
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
    CONSTRAINT `fk_schedules_created_by` 
        FOREIGN KEY (`created_by`) 
        REFERENCES `users`(`id`)
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
    CONSTRAINT `fk_schedules_updated_by` 
        FOREIGN KEY (`updated_by`) 
        REFERENCES `users`(`id`)
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
    
    -- 檢查約束：確保開始時間小於結束時間
    CONSTRAINT `chk_time_order` 
        CHECK (`start_time` < `end_time`)

) ENGINE = InnoDB 
    DEFAULT CHARSET = utf8mb4 
    COLLATE = utf8mb4_unicode_ci 
    COMMENT = '諮詢時段資料表 (修正版本：區分建立者和更新者)';

-- ===== 索引 =====
CREATE INDEX `idx_giver_id` ON `schedules` (`giver_id`);
CREATE INDEX `idx_taker_id` ON `schedules` (`taker_id`);
CREATE INDEX `idx_created_by` ON `schedules` (`created_by`);
CREATE INDEX `idx_updated_by` ON `schedules` (`updated_by`);
CREATE INDEX `idx_status` ON `schedules` (`status`);
CREATE INDEX `idx_date` ON `schedules` (`date`);

-- ===== 審計日誌表 =====
CREATE TABLE `schedule_audit_log` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY 
        COMMENT '審計日誌 ID',
    `schedule_id` INT UNSIGNED NOT NULL 
        COMMENT '關聯的時段 ID',
    `user_id` INT UNSIGNED NULL 
        COMMENT '操作者使用者 ID，可為 NULL（系統操作）',
    `user_role` ENUM('GIVER', 'TAKER', 'SYSTEM') NULL 
        COMMENT '操作者角色',
    `action` ENUM('CREATE', 'UPDATE', 'DELETE', 'STATUS_CHANGE') NOT NULL 
        COMMENT '操作類型',
    `old_values` JSON NULL 
        COMMENT '修改前的值（JSON 格式）',
    `new_values` JSON NULL 
        COMMENT '修改後的值（JSON 格式）',
    `description` VARCHAR(255) NULL 
        COMMENT '操作描述',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL 
        COMMENT '操作時間',
    
    -- 外鍵約束
    CONSTRAINT `fk_audit_schedule` 
        FOREIGN KEY (`schedule_id`) 
        REFERENCES `schedules`(`id`)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT `fk_audit_user` 
        FOREIGN KEY (`user_id`) 
        REFERENCES `users`(`id`)
        ON DELETE SET NULL 
        ON UPDATE CASCADE
    
) ENGINE = InnoDB 
    DEFAULT CHARSET = utf8mb4 
    COLLATE = utf8mb4_unicode_ci 
    COMMENT = '時段操作審計日誌表';

-- ===== 審計日誌索引 =====
CREATE INDEX `idx_audit_schedule_id` ON `schedule_audit_log` (`schedule_id`);
CREATE INDEX `idx_audit_user_id` ON `schedule_audit_log` (`user_id`);
CREATE INDEX `idx_audit_action` ON `schedule_audit_log` (`action`);
CREATE INDEX `idx_audit_created_at` ON `schedule_audit_log` (`created_at`);
CREATE INDEX `idx_audit_schedule_action` ON `schedule_audit_log` (`schedule_id`, `action`);
