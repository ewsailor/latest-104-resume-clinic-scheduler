"""
整合測試資料庫相關的測試 Fixtures。

提供整合測試用的資料庫會話和相關工具。
使用真實資料庫連線，適合端到端測試。
"""

import os

# ===== 第三方套件 =====
import pytest  # 測試框架
from sqlalchemy import create_engine  # 資料庫引擎
from sqlalchemy.orm import Session, sessionmaker  # 資料庫會話

from app.database import Base  # 資料庫基礎類別

# ===== 本地模組 =====
# 確保所有模型都被導入，這樣 Base.metadata 才會包含所有表格
from app.models import schedule, user  # noqa: F401
from app.models.schedule import Schedule  # 時段模型
from app.models.user import User  # 使用者模型


@pytest.fixture(scope="session")
def integration_db_engine():
    """
    提供整合測試用的資料庫引擎。

    使用 session scope，在整個測試會話期間共用同一個資料庫。
    適合需要真實資料庫連線的整合測試。

    Returns:
        Engine: 測試用的資料庫引擎
    """
    # 使用測試專用的 SQLite 資料庫檔案
    engine = create_engine("sqlite:///test_integration.db")

    # 建立資料表
    Base.metadata.create_all(bind=engine)

    yield engine

    # 清理：刪除測試資料庫檔案
    if os.path.exists("test_integration.db"):
        os.remove("test_integration.db")


@pytest.fixture
def integration_db_session(integration_db_engine) -> Session:
    """
    提供整合測試用的資料庫會話。

    使用真實資料庫連線，適合端到端測試。

    Args:
        integration_db_engine: 整合測試資料庫引擎

    Returns:
        Session: 整合測試用的資料庫會話
    """
    # 建立會話工廠
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=integration_db_engine
    )

    # 建立會話
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        # 清理測試資料
        session.rollback()
        session.close()


@pytest.fixture
def integration_test_data():
    """
    提供整合測試用的完整測試資料。

    Returns:
        dict: 包含多個測試實體的完整資料
    """
    return {
        "users": [
            {
                "id": 1,
                "name": "整合測試 Giver",
                "email": "giver@example.com",
                "role": "GIVER",
            },
            {
                "id": 2,
                "name": "整合測試 Taker",
                "email": "taker@example.com",
                "role": "TAKER",
            },
        ],
        "schedules": [
            {
                "id": 1,
                "giver_id": 1,
                "taker_id": None,
                "status": "AVAILABLE",
                "date": "2024-01-01",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "note": "整合測試時段 1",
            },
            {
                "id": 2,
                "giver_id": 1,
                "taker_id": 2,
                "status": "PENDING",
                "date": "2024-01-02",
                "start_time": "14:00:00",
                "end_time": "15:00:00",
                "note": "整合測試時段 2",
            },
        ],
    }
