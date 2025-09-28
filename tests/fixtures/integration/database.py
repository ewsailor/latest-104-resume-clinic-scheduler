"""整合測試資料庫 fixtures。

提供整合測試所需的資料庫相關 fixtures。
"""

# ===== 標準函式庫 =====
from datetime import date, time

# ===== 第三方套件 =====
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ===== 本地模組 =====
from app.database import Base
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.models.schedule import Schedule
from app.models.user import User


@pytest.fixture(scope="function")
def integration_db_session():
    """建立整合測試專用的資料庫會話。

    使用記憶體 SQLite 資料庫，每個測試函數都會重新建立。
    """
    # 建立記憶體 SQLite 資料庫引擎
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 建立所有表格
    Base.metadata.create_all(bind=engine)

    # 建立會話工廠
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 建立會話
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def integration_test_data(integration_db_session):
    """建立整合測試的基礎資料。

    包含測試用的使用者、時段等資料。
    """
    # 建立測試使用者
    giver_user = User(id=1, name="測試 Giver", email="giver@test.com")

    taker_user = User(id=2, name="測試 Taker", email="taker@test.com")

    system_user = User(id=3, name="系統管理員", email="system@test.com")

    # 建立測試時段
    available_schedule = Schedule(
        id=1,
        giver_id=1,
        date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(10, 0),
        status=ScheduleStatusEnum.AVAILABLE,
        note="可預約時段",
        created_by=1,
        created_by_role=UserRoleEnum.GIVER,
    )

    pending_schedule = Schedule(
        id=2,
        giver_id=1,
        taker_id=2,
        date=date(2024, 1, 16),
        start_time=time(14, 0),
        end_time=time(15, 0),
        status=ScheduleStatusEnum.PENDING,
        note="待確認時段",
        created_by=2,
        created_by_role=UserRoleEnum.TAKER,
    )

    accepted_schedule = Schedule(
        id=3,
        giver_id=1,
        taker_id=2,
        date=date(2024, 1, 17),
        start_time=time(10, 0),
        end_time=time(11, 0),
        status=ScheduleStatusEnum.ACCEPTED,
        note="已確認時段",
        created_by=1,
        created_by_role=UserRoleEnum.GIVER,
    )

    # 將資料加入資料庫
    integration_db_session.add_all(
        [
            giver_user,
            taker_user,
            system_user,
            available_schedule,
            pending_schedule,
            accepted_schedule,
        ]
    )
    integration_db_session.commit()

    return {
        "users": [giver_user, taker_user, system_user],
        "schedules": [available_schedule, pending_schedule, accepted_schedule],
        "giver_user": giver_user,
        "taker_user": taker_user,
        "system_user": system_user,
        "available_schedule": available_schedule,
        "pending_schedule": pending_schedule,
        "accepted_schedule": accepted_schedule,
    }


@pytest.fixture(scope="function")
def integration_db_override(integration_db_session):
    """覆蓋應用程式的資料庫依賴。

    讓整合測試使用測試資料庫而不是實際資料庫。
    """

    def override_get_db():
        try:
            yield integration_db_session
        finally:
            pass

    return override_get_db


@pytest.fixture(scope="function")
def integration_test_client(integration_db_session):
    """建立整合測試客戶端。

    使用測試資料庫的 FastAPI 測試客戶端。
    """
    from fastapi.testclient import TestClient

    from app.database import get_db
    from app.main import app

    def override_get_db():
        try:
            yield integration_db_session
        finally:
            pass

    # 覆蓋資料庫依賴
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    try:
        yield client
    finally:
        # 清理覆蓋
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def integration_clean_database(integration_db_session):
    """清理整合測試資料庫。

    在測試結束後清理所有資料。
    """
    yield

    # 清理所有表格
    integration_db_session.query(Schedule).delete()
    integration_db_session.query(User).delete()
    integration_db_session.commit()
