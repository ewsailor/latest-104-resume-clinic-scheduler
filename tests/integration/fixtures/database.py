"""
資料庫相關的整合測試 Fixtures。

提供整合測試用的資料庫會話、引擎和相關工具。
"""

# ===== 第三方套件 =====
import pytest  # 測試框架
from sqlalchemy import create_engine  # 資料庫引擎
from sqlalchemy.orm import Session, sessionmaker  # 資料庫會話

# ===== 本地模組 =====
# 確保所有模型都被導入，這樣 Base.metadata 才會包含所有表格
from app.models import schedule, user  # noqa: F401
from app.models.database import Base  # 資料庫基礎類別
from app.models.schedule import Schedule  # 時段模型
from app.models.user import User  # 使用者模型


@pytest.fixture(scope="class")
def integration_db_engine():
    """
    提供整合測試用的資料庫引擎。

    使用 class 範圍，在整個測試類別中共享同一個資料庫實例。

    Returns:
        Engine: 整合測試用的資料庫引擎
    """
    # 使用記憶體資料庫進行整合測試
    engine = create_engine("sqlite:///:memory:", echo=False)

    # 建立資料表
    Base.metadata.create_all(bind=engine)

    yield engine

    # 清理
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def integration_db_session(integration_db_engine):
    """
    提供整合測試用的資料庫會話。

    Args:
        integration_db_engine: 整合測試用的資料庫引擎

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
        session.close()


@pytest.fixture
def integration_db_session_with_rollback(integration_db_engine):
    """
    提供會自動回滾的整合測試資料庫會話。

    適用於需要測試事務回滾的場景。

    Args:
        integration_db_engine: 整合測試用的資料庫引擎

    Returns:
        Session: 會自動回滾的資料庫會話
    """
    # 建立會話工廠
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=integration_db_engine
    )

    # 建立會話
    session = TestingSessionLocal()

    # 開始事務
    transaction = session.begin()

    try:
        yield session
    finally:
        # 回滾事務，確保測試資料不會影響其他測試
        transaction.rollback()
        session.close()
