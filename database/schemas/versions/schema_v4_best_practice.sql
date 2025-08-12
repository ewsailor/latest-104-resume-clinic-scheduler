-- ===== 最佳實踐：schedules 表格外鍵約束設計 =====

CREATE TABLE `schedules` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY 
        COMMENT '時段 ID',
    `giver_id` INT UNSIGNED NOT NULL 
        COMMENT 'Giver ID（提供者）',
    `taker_id` INT UNSIGNED NULL 
        COMMENT 'Taker ID（預約者），可為 NULL',
    `date` DATE NOT NULL 
        COMMENT '時段日期',
    `start_time` TIME NOT NULL 
        COMMENT '開始時間',
    `end_time` TIME NOT NULL 
        COMMENT '結束時間',
    `status` VARCHAR(20) DEFAULT 'DRAFT' 
        COMMENT '時段狀態',
    `note` VARCHAR(255) NULL 
        COMMENT '備註',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL 
        COMMENT '建立時間',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL 
        COMMENT '更新時間',
    `updated_by` INT UNSIGNED NULL 
        COMMENT '最後更新者 ID',
    `updated_by_role` ENUM('GIVER', 'TAKER', 'SYSTEM') NULL 
        COMMENT '最後更新者角色',
    `deleted_at` DATETIME NULL 
        COMMENT '軟刪除標記',
    
    -- ===== 外鍵約束（最佳實踐版本） =====
    
    -- Giver 約束：考慮業務重要性
    CONSTRAINT `fk_schedules_giver` 
        FOREIGN KEY (`giver_id`) 
        REFERENCES `users`(`id`)
        ON DELETE RESTRICT      -- 保護：不能刪除有時段的 Giver
        ON UPDATE CASCADE,      -- 更新：如果 Giver ID 改變，自動同步
    
    -- Taker 約束：允許靈活性
    CONSTRAINT `fk_schedules_taker` 
        FOREIGN KEY (`taker_id`) 
        REFERENCES `users`(`id`)
        ON DELETE SET NULL      -- 靈活：Taker 刪除時設為 NULL（時段變可預約）
        ON UPDATE CASCADE,      -- 更新：如果 Taker ID 改變，自動同步
    
    -- 稽核約束：系統層面
    CONSTRAINT `fk_schedules_updated_by` 
        FOREIGN KEY (`updated_by`) 
        REFERENCES `users` (`id`) 
        ON DELETE SET NULL      -- 稽核：更新者刪除時保留記錄但設為 NULL
        ON UPDATE CASCADE,      -- 更新：自動同步 ID 變更
    
    -- ===== 業務邏輯約束 =====
    
    -- 時間邏輯檢查
    CONSTRAINT `chk_schedules_time_order` 
        CHECK (`start_time` < `end_time`),
    
    -- 日期邏輯檢查（可選）
    CONSTRAINT `chk_schedules_future_date` 
        CHECK (`date` >= CURDATE()),
    
    -- 狀態檢查（可選）
    CONSTRAINT `chk_schedules_status` 
        CHECK (`status` IN ('DRAFT', 'CONFIRMED', 'CANCELLED', 'COMPLETED'))
        
) ENGINE = InnoDB 
    DEFAULT CHARSET = utf8mb4 
    COLLATE = utf8mb4_unicode_ci 
    COMMENT = '時段資料表';

-- ===== 建議的索引設計 =====

-- 效能索引
CREATE INDEX `idx_schedules_giver_date` ON `schedules` (`giver_id`, `date`);
CREATE INDEX `idx_schedules_taker_date` ON `schedules` (`taker_id`, `date`);
CREATE INDEX `idx_schedules_status` ON `schedules` (`status`);
CREATE INDEX `idx_schedules_deleted_at` ON `schedules` (`deleted_at`);

-- 複合索引（常用查詢）
CREATE INDEX `idx_schedules_active` ON `schedules` (`deleted_at`, `status`, `date`);
