"""
資料庫相關的測試 Fixtures。

提供單元測試用的資料庫會話和相關工具。
"""

# ===== 標準函式庫 =====
import pytest  # 測試框架

# ===== 第三方套件 =====
from sqlalchemy import create_engine  # 資料庫引擎
from sqlalchemy.orm import Session, sessionmaker  # 資料庫會話

# ===== 本地模組 =====
from app.models.database import Base  # 資料庫基礎類別


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
