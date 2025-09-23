"""
單元測試使用者相關的測試 Fixtures。

提供單元測試用的使用者資料和實例。
"""

# ===== 第三方套件 =====
import pytest
from sqlalchemy.orm import Session

# ===== 本地模組 =====
from app.enums.models import UserRoleEnum
from app.models.user import User


# ===== 資料 (Data)：字典格式 =====
@pytest.fixture
def test_giver_data():
    """提供測試用的 Giver 使用者資料。"""
    return {
        "name": "測試 Giver",
        "email": "giver@example.com",
        "role": UserRoleEnum.GIVER,
    }


@pytest.fixture
def test_taker_data():
    """提供測試用的 Taker 使用者資料。"""
    return {
        "name": "測試 Taker",
        "email": "taker@example.com",
        "role": UserRoleEnum.TAKER,
    }


@pytest.fixture
def test_system_data():
    """提供測試用的系統使用者資料。"""
    return {
        "name": "系統管理員",
        "email": "system@example.com",
        "role": UserRoleEnum.SYSTEM,
    }


@pytest.fixture
def test_user_data():
    """提供測試用的通用使用者資料。

    通用使用者預設為 TAKER 角色，因為本專案目前的流程主要是 Taker 預約 Giver 時段、提供方便時段給 Giver。
    """
    return {
        "name": "測試使用者",
        "email": "test@example.com",
        "role": UserRoleEnum.TAKER,
    }


# ===== 實例 (Instance)：實例格式 =====
@pytest.fixture
def test_giver_user(db_session: Session) -> User:
    """提供測試用的 Giver 使用者實例。"""
    user = User(
        name="測試 Giver",
        email="giver@example.com",
        role=UserRoleEnum.GIVER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_taker_user(db_session: Session) -> User:
    """提供測試用的 Taker 使用者實例。"""
    user = User(
        name="測試 Taker",
        email="taker@example.com",
        role=UserRoleEnum.TAKER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user(db_session: Session) -> User:
    """提供測試用的通用使用者實例。

    通用使用者預設為 TAKER 角色，因為本專案目前的流程主要是 Taker 預約 Giver 時段、提供方便時段給 Giver。
    """
    user = User(
        name="測試使用者",
        email="test@example.com",
        role=UserRoleEnum.TAKER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_giver_and_taker(db_session: Session) -> tuple[User, User]:
    """提供測試用的 Giver 和 Taker 使用者實例。"""
    giver = User(
        name="測試 Giver",
        email="giver@example.com",
        role=UserRoleEnum.GIVER,
    )
    taker = User(
        name="測試 Taker",
        email="taker@example.com",
        role=UserRoleEnum.TAKER,
    )

    db_session.add_all([giver, taker])
    db_session.commit()

    db_session.refresh(giver)
    db_session.refresh(taker)

    return giver, taker


@pytest.fixture
def test_users(db_session: Session) -> list[User]:
    """提供多個測試用的使用者實例。

    在資料庫中建立多個測試使用者實例，並返回使用者列表。
    """
    users = [
        User(
            name="測試使用者1",
            email="test1@example.com",
            role=UserRoleEnum.TAKER,
        ),
        User(
            name="測試使用者2",
            email="test2@example.com",
            role=UserRoleEnum.TAKER,
        ),
    ]
    db_session.add_all(users)
    db_session.commit()

    for user in users:
        db_session.refresh(user)

    return users
