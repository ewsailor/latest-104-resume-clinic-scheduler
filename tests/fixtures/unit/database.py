"""
單元測試資料庫相關的測試 Fixtures。

提供單元測試用的資料庫會話和相關工具。
使用記憶體資料庫，適合快速單元測試。
"""

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


@pytest.fixture
def db_session() -> Session:
    """
    提供單元測試用的資料庫會話。

    使用記憶體 SQLite 資料庫，適合快速單元測試。
    每個測試都會獲得一個乾淨的資料庫狀態。

    Returns:
        Session: 測試用的資料庫會話
    """
    # 使用記憶體資料庫進行測試
    engine = create_engine("sqlite:///:memory:")

    # 建立資料表
    Base.metadata.create_all(bind=engine)

    # 建立會話工廠
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 建立會話
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        # 清理測試資料
        session.close()


@pytest.fixture
def test_user_data():
    """
    提供測試用的使用者資料。

    Returns:
        dict: 測試使用者資料
    """
    return {"id": 1, "name": "測試使用者", "email": "test@example.com", "role": "TAKER"}


@pytest.fixture
def test_schedule_data():
    """
    提供測試用的時段資料。

    Returns:
        dict: 測試時段資料
    """
    return {
        "id": 1,
        "giver_id": 1,
        "taker_id": None,
        "status": "AVAILABLE",
        "date": "2024-01-01",
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "note": "測試時段",
    }
