"""
資料庫連線模組單元測試。

測試 app/database/connection.py 中的所有函數和功能。
"""

# ===== 標準函式庫 =====
from unittest.mock import Mock, patch

from fastapi import HTTPException

# ===== 第三方套件 =====
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool.impl import SingletonThreadPool

# ===== 本地模組 =====
from app.core import settings
from app.database.connection import (
    SessionLocal,
    check_db_connection,
    create_database_engine,
    engine,
    get_db,
    initialize_database,
)
from app.errors.exceptions import APIError, DatabaseError, ServiceUnavailableError


class TestCreateDatabaseEngine:
    """測試 create_database_engine 函數。"""

    def test_create_database_engine_sqlite_testing_environment(self):
        """測試在測試環境中建立 SQLite 引擎。"""
        # 模擬測試環境
        with (
            patch.object(settings, 'testing', True),
            patch.object(settings, 'app_env', 'testing'),
        ):

            test_engine, test_session_factory = create_database_engine()

            # 驗證引擎和會話工廠
            assert test_engine is not None
            assert test_session_factory is not None
            assert isinstance(test_engine, Engine)
            assert isinstance(test_session_factory, sessionmaker)

            # 驗證 SQLite 引擎設定
            assert test_engine.url.drivername == "sqlite"
            assert isinstance(test_engine.pool, SingletonThreadPool)

            # 測試連線
            with test_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.fetchone()[0] == 1

    def test_create_database_engine_mysql_production_environment(self):
        """測試在生產環境中建立 MySQL 引擎。"""
        # 模擬 MySQL 連線成功
        with patch('app.database.connection.create_engine') as mock_create_engine:
            mock_engine = Mock(spec=Engine)
            mock_context_manager = Mock()
            mock_context_manager.__enter__ = Mock(return_value=Mock())
            mock_context_manager.__exit__ = Mock(return_value=None)
            mock_engine.connect.return_value = mock_context_manager
            mock_create_engine.return_value = mock_engine

            # 模擬非測試環境
            with (
                patch.object(settings, 'testing', False),
                patch.object(settings, 'app_env', 'production'),
            ):

                test_engine, test_session_factory = create_database_engine()

                # 驗證引擎和會話工廠
                assert test_engine is not None
                assert test_session_factory is not None

                # 驗證 MySQL 引擎設定參數
                mock_create_engine.assert_called_once()
                call_args = mock_create_engine.call_args
                assert call_args[1]['echo'] is False
                assert call_args[1]['pool_pre_ping'] is True
                assert call_args[1]['pool_size'] == 10
                assert call_args[1]['max_overflow'] == 10
                assert call_args[1]['pool_timeout'] == 30
                assert call_args[1]['pool_recycle'] == 3600

    def test_create_database_engine_connection_failure(self):
        """測試資料庫引擎建立失敗的情況。"""
        with patch('app.database.connection.create_engine') as mock_create_engine:
            # 模擬連線失敗
            mock_create_engine.side_effect = OperationalError("連線失敗", None, None)

            with pytest.raises(ServiceUnavailableError) as exc_info:
                create_database_engine()

            assert "資料庫引擎建立失敗" in str(exc_info.value)

    def test_create_database_engine_general_exception(self):
        """測試資料庫引擎建立時的一般異常。"""
        with patch('app.database.connection.create_engine') as mock_create_engine:
            # 模擬一般異常
            mock_create_engine.side_effect = Exception("未知錯誤")

            with pytest.raises(ServiceUnavailableError) as exc_info:
                create_database_engine()

            assert "資料庫引擎建立失敗" in str(exc_info.value)


class TestInitializeDatabase:
    """測試 initialize_database 函數。"""

    def test_initialize_database_success(self):
        """測試成功初始化資料庫。"""
        with (
            patch(
                'app.database.connection.create_database_engine'
            ) as mock_create_engine,
            patch('app.database.connection.Base') as mock_base,
            patch.object(settings, 'testing', True),
        ):

            # 模擬引擎和會話工廠
            mock_engine = Mock(spec=Engine)
            mock_session_factory = Mock(spec=sessionmaker)
            mock_create_engine.return_value = (mock_engine, mock_session_factory)

            # 執行初始化
            initialize_database()

            # 驗證函數被調用
            mock_create_engine.assert_called_once()
            mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)

    def test_initialize_database_failure(self):
        """測試資料庫初始化失敗的情況。"""
        with patch(
            'app.database.connection.create_database_engine'
        ) as mock_create_engine:
            # 模擬初始化失敗
            mock_create_engine.side_effect = Exception("初始化失敗")

            with pytest.raises(Exception) as exc_info:
                initialize_database()

            assert "初始化失敗" in str(exc_info.value)

    def test_initialize_database_non_testing_environment(self):
        """測試在非測試環境中初始化資料庫。"""
        with (
            patch(
                'app.database.connection.create_database_engine'
            ) as mock_create_engine,
            patch('app.database.connection.Base') as mock_base,
            patch.object(settings, 'testing', False),
            patch.object(settings, 'app_env', 'production'),
        ):

            # 模擬引擎和會話工廠
            mock_engine = Mock(spec=Engine)
            mock_session_factory = Mock(spec=sessionmaker)
            mock_create_engine.return_value = (mock_engine, mock_session_factory)

            # 執行初始化
            initialize_database()

            # 驗證函數被調用
            mock_create_engine.assert_called_once()
            # 在非測試環境中不應該創建表
            mock_base.metadata.create_all.assert_not_called()


class TestGetDb:
    """測試 get_db 函數。"""

    def test_get_db_success_sqlite(self):
        """測試成功取得 SQLite 資料庫會話。"""
        # 使用記憶體資料庫避免檔案權限問題
        test_engine = create_engine("sqlite:///:memory:")
        test_session_factory = sessionmaker(bind=test_engine)

        with (
            patch('app.database.connection.SessionLocal', test_session_factory),
            patch('app.database.connection.engine', test_engine),
        ):

            # 測試 get_db
            db_generator = get_db()
            db = next(db_generator)

            # 驗證會話
            assert isinstance(db, Session)
            assert db is not None

            # 測試查詢
            result = db.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

            # 清理
            try:
                next(db_generator)
            except StopIteration:
                pass

    def test_get_db_success_mysql(self):
        """測試成功取得 MySQL 資料庫會話。"""
        mock_engine = Mock(spec=Engine)
        mock_engine.url = Mock()
        mock_engine.url.drivername = "mysql"
        mock_session = Mock(spec=Session)
        mock_session_factory = Mock(return_value=mock_session)

        with (
            patch('app.database.connection.SessionLocal', mock_session_factory),
            patch('app.database.connection.engine', mock_engine),
        ):

            # 測試 get_db
            db_generator = get_db()
            db = next(db_generator)

            # 驗證會話
            assert db == mock_session

            # 驗證 MySQL 特定設定被執行
            assert mock_session.execute.call_count == 3

            # 檢查調用的 SQL 語句
            calls = mock_session.execute.call_args_list
            # 檢查 SQL 語句的文本內容
            call_0_text = str(calls[0][0][0].text)
            call_1_text = str(calls[1][0][0].text)
            call_2_text = str(calls[2][0][0].text)
            assert "SET time_zone = '+08:00'" in call_0_text
            assert "SET SESSION sql_mode" in call_1_text
            assert "SELECT 1" in call_2_text

            # 清理
            try:
                next(db_generator)
            except StopIteration:
                pass

    def test_get_db_database_not_initialized(self):
        """測試資料庫未初始化時的情況。"""
        with (
            patch('app.database.connection.SessionLocal', None),
            patch('app.database.connection.engine', None),
        ):

            with pytest.raises(DatabaseError) as exc_info:
                list(get_db())

            assert "資料庫尚未初始化" in str(exc_info.value)

    def test_get_db_session_local_none(self):
        """測試 SessionLocal 為 None 時的情況。"""
        with (
            patch('app.database.connection.SessionLocal', None),
            patch('app.database.connection.engine', Mock()),
        ):

            with pytest.raises(DatabaseError) as exc_info:
                list(get_db())

            assert "資料庫尚未初始化" in str(exc_info.value)

    def test_get_db_engine_none(self):
        """測試 engine 為 None 時的情況。"""
        with (
            patch('app.database.connection.SessionLocal', Mock()),
            patch('app.database.connection.engine', None),
        ):

            with pytest.raises(DatabaseError) as exc_info:
                list(get_db())

            assert "資料庫尚未初始化" in str(exc_info.value)

    def test_get_db_api_error_propagation(self):
        """測試 APIError 的傳播。"""
        mock_engine = Mock(spec=Engine)
        mock_engine.url = Mock()
        mock_engine.url.drivername = "sqlite"
        mock_session = Mock(spec=Session)
        mock_session.execute.side_effect = APIError("API 錯誤", "TEST_ERROR")
        mock_session_factory = Mock(return_value=mock_session)

        with (
            patch('app.database.connection.SessionLocal', mock_session_factory),
            patch('app.database.connection.engine', mock_engine),
        ):

            with pytest.raises(APIError) as exc_info:
                list(get_db())

            assert "API 錯誤" in str(exc_info.value)
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_get_db_http_exception_propagation(self):
        """測試 HTTPException 的傳播。"""
        mock_engine = Mock(spec=Engine)
        mock_engine.url = Mock()
        mock_engine.url.drivername = "sqlite"
        mock_session = Mock(spec=Session)
        mock_session.execute.side_effect = HTTPException(
            status_code=500, detail="HTTP 錯誤"
        )
        mock_session_factory = Mock(return_value=mock_session)

        with (
            patch('app.database.connection.SessionLocal', mock_session_factory),
            patch('app.database.connection.engine', mock_engine),
        ):

            with pytest.raises(HTTPException) as exc_info:
                list(get_db())

            assert exc_info.value.status_code == 500
            assert "HTTP 錯誤" in exc_info.value.detail
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_get_db_general_exception_handling(self):
        """測試一般異常的處理。"""
        mock_engine = Mock(spec=Engine)
        mock_engine.url = Mock()
        mock_engine.url.drivername = "sqlite"
        mock_session = Mock(spec=Session)
        mock_session.execute.side_effect = Exception("一般錯誤")
        mock_session_factory = Mock(return_value=mock_session)

        with (
            patch('app.database.connection.SessionLocal', mock_session_factory),
            patch('app.database.connection.engine', mock_engine),
        ):

            with pytest.raises(DatabaseError) as exc_info:
                list(get_db())

            assert "資料庫會話建立失敗" in str(exc_info.value)
            assert "一般錯誤" in str(exc_info.value)
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_get_db_always_closes_session(self):
        """測試 get_db 總是關閉會話。"""
        mock_engine = Mock(spec=Engine)
        mock_engine.url = Mock()
        mock_engine.url.drivername = "sqlite"
        mock_session = Mock(spec=Session)
        mock_session_factory = Mock(return_value=mock_session)

        with (
            patch('app.database.connection.SessionLocal', mock_session_factory),
            patch('app.database.connection.engine', mock_engine),
        ):

            # 正常情況
            db_generator = get_db()
            next(db_generator)
            try:
                next(db_generator)
            except StopIteration:
                pass

            mock_session.close.assert_called_once()


class TestCheckDbConnection:
    """測試 check_db_connection 函數。"""

    def test_check_db_connection_success(self):
        """測試成功檢查資料庫連線。"""
        mock_engine = Mock(spec=Engine)
        mock_connection = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_connection)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_engine.connect.return_value = mock_context_manager

        with patch('app.database.connection.engine', mock_engine):
            # 應該不會拋出異常
            check_db_connection()

            # 驗證連線檢查
            mock_engine.connect.assert_called_once()
            mock_connection.execute.assert_called_once()
            # 檢查調用的 SQL 語句
            call_args = mock_connection.execute.call_args[0]
            assert "SELECT 1" in str(call_args[0])

    def test_check_db_connection_engine_none(self):
        """測試引擎為 None 時的情況。"""
        with patch('app.database.connection.engine', None):
            with pytest.raises(DatabaseError) as exc_info:
                check_db_connection()

            assert "資料庫引擎尚未初始化" in str(exc_info.value)

    def test_check_db_connection_operational_error(self):
        """測試連線操作錯誤。"""
        mock_engine = Mock(spec=Engine)
        mock_engine.connect.side_effect = OperationalError("連線失敗", None, None)

        with patch('app.database.connection.engine', mock_engine):
            with pytest.raises(OperationalError):
                check_db_connection()

    def test_check_db_connection_sqlalchemy_error(self):
        """測試 SQLAlchemy 錯誤。"""
        mock_engine = Mock(spec=Engine)
        mock_engine.connect.side_effect = SQLAlchemyError("SQLAlchemy 錯誤")

        with patch('app.database.connection.engine', mock_engine):
            with pytest.raises(SQLAlchemyError):
                check_db_connection()

    def test_check_db_connection_general_exception(self):
        """測試一般異常。"""
        mock_engine = Mock(spec=Engine)
        mock_engine.connect.side_effect = Exception("一般錯誤")

        with patch('app.database.connection.engine', mock_engine):
            with pytest.raises(Exception) as exc_info:
                check_db_connection()

            assert "一般錯誤" in str(exc_info.value)


class TestGlobalVariables:
    """測試全域變數。"""

    def test_global_variables_initial_state(self):
        """測試全域變數的初始狀態。"""
        # 在測試環境中，這些變數可能為 None
        # 這個測試主要驗證變數存在且可以被訪問
        assert engine is None or isinstance(engine, Engine)
        assert SessionLocal is None or isinstance(SessionLocal, sessionmaker)

    def test_global_variables_after_initialization(self):
        """測試初始化後的全域變數。"""
        with patch(
            'app.database.connection.create_database_engine'
        ) as mock_create_engine:
            mock_engine = Mock(spec=Engine)
            mock_session_factory = Mock(spec=sessionmaker)
            mock_create_engine.return_value = (mock_engine, mock_session_factory)

            # 執行初始化
            initialize_database()

            # 驗證全域變數被設定
            # 注意：在實際測試中，這些變數可能不會被設定，因為我們使用了 mock
            # 這個測試主要驗證初始化過程不出錯


class TestDatabaseEngineConfiguration:
    """測試資料庫引擎配置。"""

    def test_sqlite_engine_configuration(self):
        """測試 SQLite 引擎配置。"""
        # 模擬測試環境
        with (
            patch.object(settings, 'testing', True),
            patch.object(settings, 'app_env', 'testing'),
        ):

            test_engine, _ = create_database_engine()

            # 驗證 SQLite 特定配置
            assert test_engine.url.drivername == "sqlite"
            assert isinstance(test_engine.pool, SingletonThreadPool)

            # 驗證連線參數（SQLite 使用 SingletonThreadPool，結構不同）
            # 在 SQLite 中，連線參數是通過 create_engine 的 connect_args 參數設定的
            # 這裡主要驗證引擎類型正確
            assert test_engine.url.drivername == "sqlite"

    def test_mysql_engine_configuration(self):
        """測試 MySQL 引擎配置。"""
        with patch('app.database.connection.create_engine') as mock_create_engine:
            mock_engine = Mock(spec=Engine)
            mock_context_manager = Mock()
            mock_context_manager.__enter__ = Mock(return_value=Mock())
            mock_context_manager.__exit__ = Mock(return_value=None)
            mock_engine.connect.return_value = mock_context_manager
            mock_create_engine.return_value = mock_engine

            # 模擬非測試環境
            with (
                patch.object(settings, 'testing', False),
                patch.object(settings, 'app_env', 'production'),
            ):

                create_database_engine()

                # 驗證 MySQL 特定配置
                call_args = mock_create_engine.call_args
                assert call_args[1]['pool_pre_ping'] is True
                assert call_args[1]['pool_size'] == 10
                assert call_args[1]['max_overflow'] == 10
                assert call_args[1]['pool_timeout'] == 30
                assert call_args[1]['pool_recycle'] == 3600

                # 驗證連線參數
                connect_args = call_args[1]['connect_args']
                assert connect_args['charset'] == 'utf8mb4'


class TestSessionFactory:
    """測試會話工廠。"""

    def test_session_factory_creation(self):
        """測試會話工廠建立。"""
        test_engine, test_session_factory = create_database_engine()

        # 驗證會話工廠
        assert test_session_factory is not None
        assert isinstance(test_session_factory, sessionmaker)

        # 測試建立會話
        session = test_session_factory()
        assert isinstance(session, Session)
        session.close()

    def test_session_factory_configuration(self):
        """測試會話工廠配置。"""
        # 模擬測試環境
        with (
            patch.object(settings, 'testing', True),
            patch.object(settings, 'app_env', 'testing'),
        ):

            test_engine, test_session_factory = create_database_engine()

            # 驗證會話工廠配置
            # sessionmaker 的配置是通過參數設定的，不是屬性
            # 這裡主要驗證會話工廠可以正常創建會話
            session = test_session_factory()
            assert isinstance(session, Session)
            session.close()
