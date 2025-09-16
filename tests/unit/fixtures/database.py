"""
資料庫相關的測試 Fixtures。

提供單元測試用的資料庫會話和相關工具。
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
    提供測試用的資料庫會話。

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
