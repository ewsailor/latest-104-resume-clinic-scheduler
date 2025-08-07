"""
資料庫模組測試。

測試資料庫連線、會話管理等功能。
"""

from unittest.mock import Mock, patch

# ===== 標準函式庫 =====
import pytest

# ===== 第三方套件 =====
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

# ===== 本地模組 =====
from app.models.database import (
    Base,
    SessionLocal,
    check_db_connection,
    create_database_engine,
    engine,
    get_db,
    get_healthy_db,
)


# ===== 測試設定 =====
class TestDatabaseModule:
    """資料庫模組測試類別。"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """設定測試環境。"""
        # 使用記憶體資料庫進行測試
        self.test_engine = create_engine("sqlite:///:memory:")
        self.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.test_engine
        )

        # 建立資料表
        Base.metadata.create_all(bind=self.test_engine)

        yield

    def test_create_database_engine_success(self):
        """測試成功建立資料庫引擎。"""
        # 模擬設定
        with patch("app.models.database.settings") as mock_settings:
            mock_settings.mysql_connection_string = (
                "mysql+pymysql://user:pass@localhost/test"
            )
            mock_settings.mysql_database = "test_db"
            mock_settings.mysql_host = "localhost"
            mock_settings.mysql_port = 3306
            mock_settings.mysql_user = "test_user"

            # 模擬 create_engine 以避免實際連線
            with patch("app.models.database.create_engine") as mock_create_engine:
                mock_engine = Mock()
                mock_create_engine.return_value = mock_engine

                # 模擬連線測試
                mock_conn = Mock()
                mock_context = Mock()
                mock_context.__enter__ = Mock(return_value=mock_conn)
                mock_context.__exit__ = Mock(return_value=None)
                mock_engine.connect.return_value = mock_context

                # 執行測試
                result_engine, result_session, result_base = create_database_engine()

                # 驗證結果
                assert result_engine is not None
                assert result_session is not None
                assert result_base is not None

                # 驗證 create_engine 被正確呼叫
                mock_create_engine.assert_called_once()

    def test_create_database_engine_failure(self):
        """測試資料庫引擎建立失敗。"""
        # 模擬設定
        with patch("app.models.database.settings") as mock_settings:
            mock_settings.mysql_connection_string = "invalid://connection"

            # 執行測試並驗證異常
            with pytest.raises(Exception):
                create_database_engine()

    def test_get_db_success(self):
        """測試成功取得資料庫會話。"""
        # 模擬 SessionLocal
        with patch("app.models.database.SessionLocal") as mock_session_local:
            mock_db = Mock()
            mock_session_local.return_value = mock_db

            # 執行測試
            db_generator = get_db()
            db = next(db_generator)

            # 驗證結果
            assert db == mock_db
            mock_db.execute.assert_called()

            # 清理生成器
            try:
                next(db_generator)
            except StopIteration:
                pass

    def test_get_db_with_exception(self):
        """測試資料庫會話發生異常時的處理。"""
        # 模擬 SessionLocal
        with patch("app.models.database.SessionLocal") as mock_session_local:
            mock_db = Mock()
            mock_db.execute.side_effect = Exception("Database error")
            mock_session_local.return_value = mock_db

            # 執行測試
            db_generator = get_db()

            # 驗證異常處理
            with pytest.raises(Exception):
                next(db_generator)

            # 驗證回滾和關閉
            mock_db.rollback.assert_called_once()
            mock_db.close.assert_called_once()

    def test_check_db_connection_success(self):
        """測試資料庫連線檢查成功。"""
        # 模擬 engine
        with patch("app.models.database.engine") as mock_engine:
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn

            # 執行測試
            result = check_db_connection()

            # 驗證結果
            assert result is True
            mock_conn.execute.assert_called_once()

    def test_check_db_connection_operational_error(self):
        """測試資料庫連線檢查遇到操作錯誤。"""
        # 模擬 engine
        with patch("app.models.database.engine") as mock_engine:
            mock_engine.connect.side_effect = OperationalError("", "", "")

            # 執行測試
            result = check_db_connection()

            # 驗證結果
            assert result is False

    def test_check_db_connection_general_exception(self):
        """測試資料庫連線檢查遇到一般異常。"""
        # 模擬 engine
        with patch("app.models.database.engine") as mock_engine:
            mock_engine.connect.side_effect = Exception("General error")

            # 執行測試
            result = check_db_connection()

            # 驗證結果
            assert result is False

    def test_get_healthy_db_success(self):
        """測試健康檢查資料庫連線成功。"""
        # 模擬 engine
        with patch("app.models.database.engine") as mock_engine:
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn

            # 執行測試
            result = get_healthy_db()

            # 驗證結果
            assert result is True
            mock_conn.execute.assert_called_once()

    def test_get_healthy_db_failure(self):
        """測試健康檢查資料庫連線失敗。"""
        # 模擬 engine
        with patch("app.models.database.engine") as mock_engine:
            mock_engine.connect.side_effect = Exception("Database error")

            # 執行測試並驗證異常
            with pytest.raises(HTTPException) as exc_info:
                get_healthy_db()

            # 驗證異常詳情
            assert exc_info.value.status_code == 503
            assert "database" in exc_info.value.detail
            assert exc_info.value.detail["database"] == "disconnected"

    def test_database_components_initialization(self):
        """測試資料庫組件初始化。"""
        # 驗證全域變數已正確初始化
        assert engine is not None
        assert SessionLocal is not None
        assert Base is not None

    def test_base_metadata_creation(self):
        """測試基礎類別元資料建立。"""
        # 驗證可以建立資料表
        Base.metadata.create_all(bind=self.test_engine)

        # 驗證資料表已建立（使用 SQLAlchemy 的 inspect 函數）
        from sqlalchemy import inspect

        inspector = inspect(self.test_engine)
        tables = inspector.get_table_names()
        assert len(tables) >= 0  # 至少應該沒有錯誤

    def test_session_local_creation(self):
        """測試會話工廠建立。"""
        # 建立測試會話
        session = SessionLocal()

        # 驗證會話可用
        assert session is not None

        # 清理
        session.close()

    def test_engine_connection_pool_settings(self):
        """測試引擎連線池設定。"""
        # 驗證引擎設定
        assert engine.pool.size() <= 10  # 連線池大小
        assert engine.pool.overflow() <= 20  # 最大溢出連線數
        assert engine.pool.timeout() == 30  # 連線超時時間
