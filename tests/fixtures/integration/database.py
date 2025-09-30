"""整合測試資料庫 fixtures。

注意：理想情況下應使用 MySQL 提供整合測試所需的資料庫相關 fixtures，
確保與生產環境一致。但為了測試隔離和速度，目前使用 SQLite 記憶體資料庫。
生產環境部署前應切換回 MySQL 進行完整整合測試。
"""

# ===== 第三方套件 =====
import tempfile

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ===== 本地模組 =====
from app.core import settings  # TODO: 切換回 MySQL 時需要取消註解
from app.database import Base, get_db
from app.factory import create_templates
from app.middleware.error_handler import setup_error_handlers
from app.models import Schedule, User  # 導入所有模型
from app.routers import api_router, health_router, main_router


@pytest.fixture(scope="function")
def integration_db_session():
    """建立整合測試專用的資料庫會話。

    注意：目前使用 SQLite 記憶體資料庫確保測試隔離。
    生產環境部署前應切換回 MySQL 進行完整整合測試。

    Returns:
        Session: SQLAlchemy 資料庫會話實例，用於整合測試
    """
    # TODO: 生產環境部署前應切換回 MySQL
    # database_url = settings.mysql_connection_string  # MySQL 連接字串

    # 使用臨時檔案資料庫，避免記憶體資料庫的會話隔離問題
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    database_url = f"sqlite:///{temp_db.name}"

    # 建立 SQLite 引擎
    engine = create_engine(
        database_url,
        echo=False,  # 關閉 SQL 查詢日誌，避免測試輸出過於冗長
        pool_pre_ping=False,  # SQLite 不需要連線檢查
        connect_args={
            "check_same_thread": False
        },  # 允許不同執行緒共用同一個資料庫連線，因為 FastAPI 測試時，API 請求和資料庫 session 可能不在同一個執行緒
    )

    # 在記憶體 DB 中，根據 SQLAlchemy 模型定義，建立對應的資料庫表結構
    # 需要導入所有模型，確保 Base.metadata 包含所有表定義

    # 確保所有模型都被正確導入，以便 Base.metadata 包含所有表定義
    # 這很重要，因為 SQLAlchemy 需要知道所有表結構才能創建表
    Base.metadata.create_all(bind=engine)

    # 建立會話工廠：每次呼叫 TestingSessionLocal()，就生成一個新 Session 實例
    # 確保每個請求，都有一個獨立的資料庫連線，避免共用連線，導致資料庫操作錯亂
    TestingSessionLocal = sessionmaker(
        bind=engine,  # 指定 Session 連線的資料庫引擎（engine）
        autocommit=False,  # 不自動提交，手動呼叫 .commit() 才會儲存資料
        autoflush=False,  # 不自動刷新、不自動將未提交的改動同步到資料庫，需手動呼叫 flush()
    )

    # 建立會話實例
    session = TestingSessionLocal()

    try:
        # TODO: 切換回 MySQL 時需要恢復以下配置
        # session.execute(text("SET time_zone = '+08:00'"))
        # session.execute(
        #     text(
        #         "SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'"
        #     )
        # )
        # session.commit()

        # 使用 yield 確保會話在測試結束後正確關閉
        yield session
    except Exception as e:
        # 錯誤處理：會話操作失敗時回滾並重新拋出異常
        session.rollback()
        raise Exception(f"整合測試資料庫會話操作失敗：{str(e)}")
    finally:
        # 確保會話在測試結束後正確關閉，避免資源洩漏
        session.close()


@pytest.fixture(scope="function")
def integration_db_override(integration_db_session):
    """覆蓋應用程式的資料庫依賴。

    讓整合測試使用測試資料庫而不是實際資料庫。
    這個 fixture 提供了一個可以覆蓋 FastAPI 依賴注入的函數。

    Args:
        integration_db_session: 整合測試專用的資料庫會話

    Returns:
        function: 覆蓋 get_db 的函數
    """

    def override_get_db():
        """覆蓋 get_db 的函數，直接返回測試會話。"""
        try:
            yield integration_db_session
        finally:
            pass

    return override_get_db


@pytest.fixture(scope="function")
def integration_test_client(integration_db_session):
    """建立整合測試專用的 FastAPI 測試客戶端。

    這個 fixture 創建一個獨立的 FastAPI 應用程式實例，專門用於整合測試。
    它使用測試專用的資料庫會話，確保測試不會影響生產環境的資料庫。

    Args:
        integration_db_session: 整合測試專用的資料庫會話

    Yields:
        TestClient: FastAPI 測試客戶端，用於發送 HTTP 請求
    """
    # 創建新的應用程式實例，避免使用全域 app（已連接到真實 MySQL）
    # 注意：不調用 create_app(settings)，因為它會重新初始化資料庫
    test_app = FastAPI()

    # 設定模板引擎實例
    templates = create_templates(settings)

    # 將 templates 設定到應用程式狀態中，用依賴注入解決循環匯入問題
    test_app.state.templates = templates

    # 設定錯誤處理器，確保測試中的錯誤能正確處理
    setup_error_handlers(test_app)

    # 註冊所有路由，確保測試能訪問完整的 API 功能
    test_app.include_router(main_router)  # 主要路由（首頁等）
    test_app.include_router(health_router)  # 健康檢查路由
    test_app.include_router(api_router)  # API 路由

    # 覆寫資料庫連線的依賴注入，確保 API 呼叫的 DB 是測試 DB
    # 直接使用 integration_db_session，而不是創建新的會話
    def override_get_db():
        """覆蓋 get_db 依賴，使用測試專用的資料庫會話。"""
        # 確保使用同一個會話實例
        yield integration_db_session

    # 使用 FastAPI 的依賴注入覆蓋機制
    test_app.dependency_overrides[get_db] = override_get_db

    # 創建測試客戶端並提供給測試使用
    with TestClient(test_app) as client:
        yield client

    # 測試結束後，清除依賴注入的覆寫，避免影響其他測試
    test_app.dependency_overrides.clear()
