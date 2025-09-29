"""整合測試資料庫 fixtures。

注意：理想情況下應使用 MySQL 提供整合測試所需的資料庫相關 fixtures，
確保與生產環境一致。但為了測試隔離和速度，目前使用 SQLite 記憶體資料庫。
生產環境部署前應切換回 MySQL 進行完整整合測試。
"""

# ===== 第三方套件 =====
# isort: off
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# isort: on

from app.core import settings

# ===== 本地模組 =====
# from app.core import settings  # TODO: 切換回 MySQL 時需要取消註解
from app.database import Base, get_db
from app.factory import create_app


@pytest.fixture(scope="function")
def integration_db_session():
    """建立整合測試專用的資料庫會話。

    注意：目前使用 SQLite 記憶體資料庫確保測試隔離。
    生產環境部署前應切換回 MySQL 進行完整整合測試。
    """
    # TODO: 生產環境部署前應切換回 MySQL
    # database_url = settings.mysql_connection_string  # MySQL 連接字串

    # 使用 SQLite 記憶體資料庫，確保測試隔離
    database_url = "sqlite:///:memory:"

    # 建立 SQLite 記憶體引擎
    engine = create_engine(
        database_url,
        echo=False,  # 關閉 SQL 查詢日誌
        connect_args={"check_same_thread": False},  # SQLite 特定參數
    )

    # 建立所有表格
    Base.metadata.create_all(bind=engine)

    # 建立會話工廠：每次呼叫 TestingSessionLocal()，就生成一個新 Session 實例，確保每個請求，都有一個獨立的資料庫連線，避免共用連線，導致資料庫操作錯亂
    TestingSessionLocal = sessionmaker(
        bind=engine,  # 指定 Session 連線的資料庫引擎（engine）
        autocommit=False,  # 不自動提交，手動呼叫 .commit() 才會儲存資料
        autoflush=False,  # 不自動刷新、不自動將未提交的改動同步到資料庫，需手動呼叫 flush()
    )

    # 建立會話
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

        yield session
    except Exception as e:
        # 錯誤處理：會話操作失敗時回滾並重新拋出異常
        session.rollback()
        raise Exception(f"整合測試資料庫會話操作失敗：{str(e)}")
    finally:
        session.close()


def create_override_get_db(session):
    """建立覆寫 get_db 的函式工廠。"""

    def override_get_db():
        try:
            yield session
        finally:
            pass

    return override_get_db


@pytest.fixture(scope="function")
def integration_db_override(integration_db_session):
    """覆蓋應用程式的資料庫依賴。

    讓整合測試使用測試資料庫而不是實際資料庫。
    """
    return create_override_get_db(integration_db_session)


@pytest.fixture(scope="function")
def integration_test_client(integration_db_session):
    """建立整合測試專用的 FastAPI 測試客戶端。"""
    # 創建新的應用程式實例，避免使用全域 app（已連接到真實 MySQL）
    test_app = create_app(settings)

    # 覆寫資料庫連線的依賴注入，確保 API 呼叫的 DB 是測試 DB
    test_app.dependency_overrides[get_db] = create_override_get_db(
        integration_db_session
    )

    with TestClient(test_app) as client:
        yield client

    # 測試結束後，清除依賴注入的覆寫
    test_app.dependency_overrides.clear()
