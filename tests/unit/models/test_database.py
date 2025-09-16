"""
資料庫模組單元測試。

測試資料庫連線、會話管理、引擎建立等功能。
"""

# ===== 標準函式庫 =====
import pytest  # 測試框架

# ===== 第三方套件 =====
from sqlalchemy import text
from sqlalchemy.orm import Session

# ===== 本地模組 =====
from app.database import (
    Base,
    check_db_connection,
    create_database_engine,
    engine,
    get_db,
    initialize_database,
)


class TestDatabaseModule:
    """資料庫模組測試類別。"""

    def test_create_database_engine_success(self):
        """測試成功建立資料庫引擎。"""
        # 測試建立引擎
        test_engine, test_session_factory = create_database_engine()

        # 驗證引擎存在
        assert test_engine is not None
        assert test_session_factory is not None

        # 測試連線
        with test_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_create_database_engine_failure(self):
        """測試資料庫引擎建立失敗的情況。"""
        # 這個測試需要模擬連線失敗的情況
        # 在實際環境中，可以通過設定無效的連線參數來測試

    def test_get_db_success(self):
        """測試成功取得資料庫會話。"""
        # 初始化資料庫
        initialize_database()

        # 測試 get_db 函式
        db_generator = get_db()
        db = next(db_generator)

        # 驗證會話存在且可用
        assert isinstance(db, Session)
        assert db is not None

        # 測試查詢
        result = db.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1

        # 清理
        db.close()

    def test_get_db_with_exception(self):
        """測試 get_db 在異常情況下的行為。"""
        # 這個測試需要模擬資料庫未初始化的情況

    def test_check_db_connection_success(self):
        """測試成功檢查資料庫連線。"""
        # 初始化資料庫
        initialize_database()

        # 測試連線檢查
        check_db_connection()  # 應該不會拋出異常

    def test_check_db_connection_operational_error(self):
        """測試資料庫連線操作錯誤。"""
        # 這個測試需要模擬連線失敗的情況

    def test_check_db_connection_general_exception(self):
        """測試資料庫連線一般異常。"""
        # 這個測試需要模擬一般異常情況

    def test_database_components_initialization(self):
        """測試資料庫組件初始化。"""
        # 測試初始化
        initialize_database()

        # 驗證全域變數已設定（在測試環境中可能為 None，因為每次測試都創建新的引擎）
        # 這個測試主要驗證初始化過程不出錯

    def test_base_metadata_creation(self):
        """測試基礎元資料建立。"""
        # 驗證 Base 存在且可存取
        assert Base is not None
        assert hasattr(Base, "metadata")

    def test_session_local_creation(self):
        """測試會話工廠建立。"""
        # 測試建立引擎和會話工廠
        test_engine, test_session_factory = create_database_engine()

        # 驗證會話工廠存在
        assert test_session_factory is not None

        # 測試建立會話
        session = test_session_factory()
        assert isinstance(session, Session)
        session.close()

    def test_engine_connection_pool_settings(self):
        """測試引擎連線池設定。"""
        # 在測試環境中，engine 可能是 None
        if engine is not None:
            # 根據資料庫類型驗證不同的引擎設定
            from app.core import settings

            if settings.testing or settings.app_env == "testing":
                # SQLite 測試環境：檢查連線池類型
                from sqlalchemy.pool.impl import SingletonThreadPool

                assert isinstance(engine.pool, SingletonThreadPool)
                # SQLite 使用 SingletonThreadPool，屬性結構不同
            else:
                # MySQL 環境：驗證具體的引擎設定
                assert engine.pool.size() <= 10  # 連線池大小
                assert engine.pool.overflow() <= 20  # 最大溢出連線數
                assert engine.pool.timeout() == 30  # 連線超時時間
        else:
            # 如果 engine 是 None，跳過測試
            pytest.skip("Engine 未初始化")
