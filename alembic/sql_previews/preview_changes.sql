CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> c6dd3264fae3

INSERT INTO alembic_version (version_num) VALUES ('c6dd3264fae3');

-- Running upgrade c6dd3264fae3 -> e163214703ee

ALTER TABLE schedules DROP FOREIGN KEY fk_giver;

ALTER TABLE schedules DROP FOREIGN KEY fk_taker;

DROP INDEX idx_schedule_giver_date ON schedules;

DROP INDEX idx_schedule_taker_date ON schedules;

DROP INDEX idx_taker_id ON schedules;

CREATE INDEX ix_schedules_id ON schedules (id);

ALTER TABLE schedules COMMENT '';

ALTER TABLE users CHANGE created_at created_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間';

ALTER TABLE users CHANGE updated_at updated_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間';

ALTER TABLE users CHANGE deleted_at deleted_at DATETIME NULL COMMENT '軟刪除標記';

DROP INDEX idx_deleted_at ON users;

DROP INDEX idx_email ON users;

CREATE INDEX ix_users_id ON users (id);

ALTER TABLE users COMMENT '';

UPDATE alembic_version SET version_num='e163214703ee' WHERE alembic_version.version_num = 'c6dd3264fae3';

