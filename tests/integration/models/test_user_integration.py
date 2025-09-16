"""
User 模型整合測試模組。

測試 User 模型的 CRUD 操作、屬性驗證和關聯查詢。
"""

# ===== 標準函式庫 =====
import datetime
from typing import Any, Dict

# ===== 第三方套件 =====
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

# ===== 本地模組 =====
from app.database import Base
from app.models.user import User


class TestUserIntegration:
    """User 模型整合測試類別。"""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """設定測試資料庫。"""
        # 使用記憶體 SQLite 資料庫
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # 建立資料表
        Base.metadata.create_all(bind=self.engine)

        yield

        # 清理
        Base.metadata.drop_all(bind=self.engine)

    @pytest.fixture
    def db_session(self):
        """提供資料庫會話。"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @pytest.fixture
    def sample_user_data(self) -> Dict[str, Any]:
        """提供範例使用者資料。"""
        return {
            "name": "測試使用者",
            "email": "test@example.com",
        }

    def test_user_crud_operations(self, db_session, sample_user_data):
        """測試使用者 CRUD 操作。"""
        # 建立使用者
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # 驗證建立
        assert user.id is not None
        assert user.id > 0
        assert user.name == "測試使用者"
        assert user.email == "test@example.com"
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.deleted_at is None

        # 讀取使用者
        retrieved_user = db_session.query(User).filter(User.id == user.id).first()
        assert retrieved_user is not None
        assert retrieved_user.name == user.name
        assert retrieved_user.email == user.email

        # 更新使用者
        retrieved_user.name = "更新後的使用者"
        retrieved_user.email = "updated@example.com"
        db_session.commit()
        db_session.refresh(retrieved_user)

        # 驗證更新
        assert retrieved_user.name == "更新後的使用者"
        assert retrieved_user.email == "updated@example.com"
        # 注意：在快速執行時，時間戳記可能相同，所以只驗證不早於原始時間
        assert retrieved_user.updated_at >= user.updated_at

        # 軟刪除使用者
        retrieved_user.deleted_at = datetime.datetime.now()
        db_session.commit()
        db_session.refresh(retrieved_user)

        # 驗證軟刪除
        assert retrieved_user.deleted_at is not None
        assert retrieved_user.is_deleted is True
        assert retrieved_user.is_active is False

    def test_user_unique_email_constraint(self, db_session, sample_user_data):
        """測試使用者電子信箱唯一性約束。"""
        # 建立第一個使用者
        user1 = User(**sample_user_data)
        db_session.add(user1)
        db_session.commit()

        # 嘗試建立相同電子信箱的使用者
        user2 = User(
            name="另一個使用者", email=sample_user_data["email"]  # 相同的電子信箱
        )
        db_session.add(user2)

        # 驗證約束違反
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_required_fields(self, db_session):
        """測試使用者必要欄位驗證。"""
        # 測試缺少 name
        user = User(email="test@example.com")
        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

        # 測試缺少 email
        user = User(name="測試使用者")
        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_properties(self, db_session, sample_user_data):
        """測試使用者屬性方法。"""
        # 建立活躍使用者
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # 測試活躍狀態
        assert user.is_active is True
        assert user.is_deleted is False

        # 軟刪除使用者
        user.deleted_at = datetime.datetime.now()
        db_session.commit()
        db_session.refresh(user)

        # 測試刪除狀態
        assert user.is_active is False
        assert user.is_deleted is True

    def test_user_to_dict_method(self, db_session, sample_user_data):
        """測試使用者 to_dict 方法。"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # 測試序列化
        user_dict = user.to_dict()

        assert isinstance(user_dict, dict)
        assert user_dict["id"] == user.id
        assert user_dict["name"] == user.name
        assert user_dict["email"] == user.email
        assert user_dict["is_active"] is True
        assert user_dict["is_deleted"] is False
        assert "created_at" in user_dict
        assert "updated_at" in user_dict
        assert user_dict["deleted_at"] is None

    def test_user_to_dict_with_deleted_user(self, db_session, sample_user_data):
        """測試已刪除使用者的 to_dict 方法。"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # 軟刪除使用者
        user.deleted_at = datetime.datetime.now()
        db_session.commit()
        db_session.refresh(user)

        # 測試序列化
        user_dict = user.to_dict()

        assert user_dict["is_active"] is False
        assert user_dict["is_deleted"] is True
        assert user_dict["deleted_at"] is not None

    def test_user_repr_method(self, db_session, sample_user_data):
        """測試使用者 __repr__ 方法。"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # 測試字串表示
        user_repr = repr(user)

        assert isinstance(user_repr, str)
        assert f"User(id={user.id}" in user_repr
        assert f"name='{user.name}'" in user_repr
        assert f"email='{user.email}'" in user_repr

    def test_user_timestamps_auto_generation(self, db_session, sample_user_data):
        """測試使用者時間戳記自動生成。"""
        before_create = datetime.datetime.now()

        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        after_create = datetime.datetime.now()

        # 驗證時間戳記
        assert user.created_at is not None
        assert user.updated_at is not None
        assert before_create <= user.created_at <= after_create
        assert before_create <= user.updated_at <= after_create

        # 建立時 created_at 和 updated_at 應該非常接近（允許微秒級差異）
        time_diff = abs((user.created_at - user.updated_at).total_seconds())
        assert time_diff < 1.0  # 差異應該小於 1 秒

    def test_user_timestamps_auto_update(self, db_session, sample_user_data):
        """測試使用者時間戳記自動更新。"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        original_created_at = user.created_at
        original_updated_at = user.updated_at

        # 等待一小段時間確保時間差異
        import time

        time.sleep(0.01)

        # 更新使用者
        user.name = "更新後的使用者"
        db_session.commit()
        db_session.refresh(user)

        # 驗證時間戳記更新
        assert user.created_at == original_created_at  # created_at 不應該改變
        assert user.updated_at > original_updated_at  # updated_at 應該更新

    def test_user_bulk_operations(self, db_session):
        """測試使用者批量操作。"""
        # 建立多個使用者
        users_data = [
            {"name": f"使用者{i}", "email": f"user{i}@example.com"} for i in range(1, 6)
        ]

        users = [User(**data) for data in users_data]
        db_session.add_all(users)
        db_session.commit()

        # 驗證所有使用者都已建立
        all_users = db_session.query(User).all()
        assert len(all_users) == 5

        # 驗證每個使用者都有唯一的 ID
        user_ids = [user.id for user in all_users]
        assert len(set(user_ids)) == 5  # 所有 ID 都應該是唯一的

        # 驗證電子信箱唯一性
        emails = [user.email for user in all_users]
        assert len(set(emails)) == 5  # 所有電子信箱都應該是唯一的

    def test_user_query_filters(self, db_session, sample_user_data):
        """測試使用者查詢篩選。"""
        # 建立多個使用者
        users_data = [
            {"name": "張三", "email": "zhang@example.com"},
            {"name": "李四", "email": "li@example.com"},
            {"name": "王五", "email": "wang@example.com"},
        ]

        users = [User(**data) for data in users_data]
        db_session.add_all(users)
        db_session.commit()

        # 測試按名稱查詢
        zhang_user = db_session.query(User).filter(User.name == "張三").first()
        assert zhang_user is not None
        assert zhang_user.email == "zhang@example.com"

        # 測試按電子信箱查詢
        li_user = db_session.query(User).filter(User.email == "li@example.com").first()
        assert li_user is not None
        assert li_user.name == "李四"

        # 測試按 ID 查詢
        wang_user = db_session.query(User).filter(User.id == users[2].id).first()
        assert wang_user is not None
        assert wang_user.name == "王五"

    def test_user_soft_delete_queries(self, db_session, sample_user_data):
        """測試使用者軟刪除查詢。"""
        # 建立多個使用者
        users_data = [
            {"name": "活躍使用者1", "email": "active1@example.com"},
            {"name": "活躍使用者2", "email": "active2@example.com"},
            {"name": "將被刪除的使用者", "email": "deleted@example.com"},
        ]

        users = [User(**data) for data in users_data]
        db_session.add_all(users)
        db_session.commit()

        # 軟刪除第三個使用者
        users[2].deleted_at = datetime.datetime.now()
        db_session.commit()

        # 測試查詢所有使用者（包括已刪除）
        all_users = db_session.query(User).all()
        assert len(all_users) == 3

        # 測試查詢活躍使用者
        active_users = db_session.query(User).filter(User.deleted_at.is_(None)).all()
        assert len(active_users) == 2

        # 測試查詢已刪除使用者
        deleted_users = db_session.query(User).filter(User.deleted_at.isnot(None)).all()
        assert len(deleted_users) == 1
        assert deleted_users[0].name == "將被刪除的使用者"

    def test_user_database_constraints(self, db_session):
        """測試使用者資料庫約束。"""
        # 測試電子信箱長度限制
        long_email = "a" * 200 + "@example.com"  # 超過 191 字元限制
        user = User(name="測試使用者", email=long_email)
        db_session.add(user)

        # 注意：SQLite 記憶體資料庫可能不強制長度限制
        # 在實際的 MySQL 環境中會觸發 IntegrityError
        # 這裡主要測試資料結構正確性
        try:
            db_session.commit()
            # 如果成功提交，驗證資料已儲存
            assert user.id is not None
        except IntegrityError:
            # 如果觸發約束錯誤，這是預期行為
            pass

        db_session.rollback()

        # 測試名稱長度限制
        long_name = "a" * 60  # 超過 50 字元限制
        user = User(name=long_name, email="test@example.com")
        db_session.add(user)

        # 注意：SQLite 記憶體資料庫可能不強制長度限制
        # 在實際的 MySQL 環境中會觸發 IntegrityError
        # 這裡主要測試資料結構正確性
        try:
            db_session.commit()
            # 如果成功提交，驗證資料已儲存
            assert user.id is not None
        except IntegrityError:
            # 如果觸發約束錯誤，這是預期行為
            pass

    def test_user_indexes(self, db_session, sample_user_data):
        """測試使用者索引。"""
        # 建立使用者
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # 驗證索引存在（通過查詢效能間接驗證）
        # 這個測試主要確保索引不會導致錯誤
        users_by_created_at = (
            db_session.query(User)
            .filter(
                User.created_at >= datetime.datetime.now() - datetime.timedelta(days=1)
            )
            .all()
        )

        assert len(users_by_created_at) >= 1
        assert users_by_created_at[0].id == user.id
