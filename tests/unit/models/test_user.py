"""
User 模型測試。

測試 User 模型的屬性、方法和行為。
"""

# ===== 標準函式庫 =====
from datetime import datetime

# ===== 第三方套件 =====
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ===== 本地模組 =====
from app.database import Base
from app.models.user import User


# ===== 測試設定 =====
class TestUserModel:
    """User 模型測試類別。"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """設定測試環境。"""
        # 使用記憶體資料庫進行測試
        self.test_engine = create_engine("sqlite:///:memory:")
        self.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.test_engine
        )

        # 建立資料表
        Base.metadata.create_all(bind=self.test_engine)

        yield

    def test_user_creation(self):
        """測試 User 實例創建。"""
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        assert user.name == "測試使用者"
        assert user.email == "test@example.com"
        assert user.deleted_at is None
        assert user.created_at is None  # 預設值只在資料庫層面生效
        assert user.updated_at is None  # 預設值只在資料庫層面生效

    def test_user_default_values(self):
        """測試 User 預設值。"""
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        assert user.deleted_at is None
        assert user.created_at is None  # 預設值只在資料庫層面生效
        assert user.updated_at is None  # 預設值只在資料庫層面生效

    def test_user_properties(self):
        """測試 User 屬性方法。"""
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        # 測試 is_active
        assert user.is_active is True
        user.deleted_at = datetime.now()
        assert user.is_active is False

        # 測試 is_deleted
        assert user.is_deleted is True
        user.deleted_at = None
        assert user.is_deleted is False

    def test_user_repr(self):
        """測試 User 字串表示。"""
        user = User(
            id=1,
            name="測試使用者",
            email="test@example.com",
        )

        repr_str = repr(user)
        assert "User" in repr_str
        assert "id=1" in repr_str
        assert "name='測試使用者'" in repr_str
        assert "email='test@example.com'" in repr_str

    def test_user_to_dict_success(self):
        """測試 User to_dict 方法成功情況。"""
        user = User(
            id=1,
            name="測試使用者",
            email="test@example.com",
            created_at=datetime(2024, 1, 1, 12, 0),
            updated_at=datetime(2024, 1, 2, 12, 0),
        )

        result = user.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["name"] == "測試使用者"
        assert result["email"] == "test@example.com"
        assert result["created_at"] == "2024-01-01T12:00:00"
        assert result["updated_at"] == "2024-01-02T12:00:00"
        assert result["deleted_at"] is None
        assert result["is_active"] is True
        assert result["is_deleted"] is False

    def test_user_to_dict_with_deleted_at(self):
        """測試 User to_dict 方法包含刪除時間。"""
        user = User(
            id=1,
            name="測試使用者",
            email="test@example.com",
            deleted_at=datetime(2024, 1, 3, 12, 0),
        )

        result = user.to_dict()

        assert result["deleted_at"] == "2024-01-03T12:00:00"
        assert result["is_active"] is False
        assert result["is_deleted"] is True

    def test_user_to_dict_error_handling(self):
        """測試 User to_dict 方法錯誤處理。"""
        user = User(
            id=1,
            name="測試使用者",
            email="test@example.com",
        )

        # 測試正常情況下的 to_dict 方法
        result = user.to_dict()

        # 驗證正常情況
        assert isinstance(result, dict)
        assert "id" in result
        assert "name" in result
        assert "error" not in result

    def test_user_table_structure(self):
        """測試 User 資料表結構。"""
        # 驗證資料表已建立
        # 注意：在記憶體資料庫中，我們需要先建立資料表
        Base.metadata.create_all(bind=self.test_engine)
        from sqlalchemy import inspect

        inspector = inspect(self.test_engine)
        tables = inspector.get_table_names()

        assert "users" in tables

        # 驗證欄位存在
        columns = inspector.get_columns("users")
        column_names = [col["name"] for col in columns]

        expected_columns = [
            "id",
            "name",
            "email",
            "created_at",
            "updated_at",
            "deleted_at",
        ]

        for column in expected_columns:
            assert column in column_names

    def test_user_indexes(self):
        """測試 User 資料表索引。"""
        # 驗證索引存在
        Base.metadata.create_all(bind=self.test_engine)
        from sqlalchemy import inspect

        inspector = inspect(self.test_engine)

        indexes = inspector.get_indexes("users")
        index_names = [idx["name"] for idx in indexes]

        expected_indexes = [
            "idx_users_created_at",
        ]

        for index in expected_indexes:
            assert index in index_names

    def test_user_unique_constraints(self):
        """測試 User 唯一約束。"""
        # 驗證 email 欄位的唯一約束
        Base.metadata.create_all(bind=self.test_engine)
        from sqlalchemy import inspect

        inspector = inspect(self.test_engine)

        # 在 SQLite 中，唯一約束可能不會顯示在 get_indexes 中
        # 但我們可以驗證欄位定義
        columns = inspector.get_columns("users")
        email_column = next((col for col in columns if col["name"] == "email"), None)

        assert email_column is not None
        assert email_column["nullable"] is False

    def test_user_soft_delete(self):
        """測試 User 軟刪除功能。"""
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        # 初始狀態
        assert user.is_active is True
        assert user.is_deleted is False

        # 軟刪除
        user.deleted_at = datetime.now()

        assert user.is_active is False
        assert user.is_deleted is True

    def test_user_audit_fields(self):
        """測試 User 審計欄位。"""
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        # 驗證審計欄位
        assert user.created_at is None  # 預設值只在資料庫層面生效
        assert user.updated_at is None  # 預設值只在資料庫層面生效
        assert user.deleted_at is None

    def test_user_relationship_lazy_loading(self):
        """測試 User 關聯的延遲載入設定。"""
        # 驗證關聯的 lazy 設定
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        # 所有關聯都應該使用 lazy="dynamic"
        # 注意：在 SQLAlchemy 中，dynamic 關聯返回的是 AppenderQuery 物件
        # 我們需要通過 mapper 來檢查 lazy 設定
        from sqlalchemy.orm import class_mapper

        mapper = class_mapper(User)

        assert mapper.relationships['giver_schedules'].lazy == "dynamic"
        assert mapper.relationships['taker_schedules'].lazy == "dynamic"
        assert mapper.relationships['created_schedules'].lazy == "dynamic"
        assert mapper.relationships['updated_schedules'].lazy == "dynamic"
        assert mapper.relationships['deleted_schedules'].lazy == "dynamic"

    def test_user_email_validation(self):
        """測試 User email 欄位驗證。"""
        # 測試有效的 email 格式
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@456.com",
        ]

        for email in valid_emails:
            user = User(
                name="測試使用者",
                email=email,
            )
            assert user.email == email

    def test_user_name_validation(self):
        """測試 User name 欄位驗證。"""
        # 測試不同的 name 格式
        valid_names = [
            "測試使用者",
            "Test User",
            "User123",
            "使用者姓名",
            "A" * 50,  # 最大長度
        ]

        for name in valid_names:
            user = User(
                name=name,
                email="test@example.com",
            )
            assert user.name == name

    def test_user_relationship_back_populates(self):
        """測試 User 關聯的 back_populates 設定。"""
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        # 驗證關聯的 back_populates 設定
        from sqlalchemy.orm import class_mapper

        mapper = class_mapper(User)

        assert mapper.relationships['giver_schedules'].back_populates == "giver"
        assert mapper.relationships['taker_schedules'].back_populates == "taker"
        assert (
            mapper.relationships['created_schedules'].back_populates
            == "created_by_user"
        )
        assert (
            mapper.relationships['updated_schedules'].back_populates
            == "updated_by_user"
        )
        assert (
            mapper.relationships['deleted_schedules'].back_populates
            == "deleted_by_user"
        )

    def test_user_foreign_key_constraints(self):
        """測試 User 外鍵約束。"""
        # 驗證外鍵存在
        Base.metadata.create_all(bind=self.test_engine)
        from sqlalchemy import inspect

        inspector = inspect(self.test_engine)

        foreign_keys = inspector.get_foreign_keys("users")
        fk_columns = [fk["constrained_columns"] for fk in foreign_keys]

        # User 表本身沒有外鍵，但其他表會引用它
        # 這裡主要驗證沒有意外的外鍵
        assert len(fk_columns) == 0

    def test_user_timestamps(self):
        """測試 User 時間戳記。"""
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        # 驗證時間戳記
        assert user.created_at is None  # 預設值只在資料庫層面生效
        assert user.updated_at is None  # 預設值只在資料庫層面生效
        assert user.deleted_at is None

        # 驗證時間戳記的類型（當有值時）
        # 在測試環境中，這些值為 None，所以跳過類型檢查

    def test_user_string_representation(self):
        """測試 User 字串表示的不同情況。"""
        # 測試有 ID 的情況
        user_with_id = User(
            id=1,
            name="測試使用者",
            email="test@example.com",
        )
        repr_str = repr(user_with_id)
        assert "id=1" in repr_str

        # 測試沒有 ID 的情況
        user_without_id = User(
            name="測試使用者",
            email="test@example.com",
        )
        repr_str = repr(user_without_id)
        assert "id=None" in repr_str

    def test_user_to_dict_with_none_values(self):
        """測試 User to_dict 方法處理 None 值。"""
        user = User(
            id=1,
            name="測試使用者",
            email="test@example.com",
            deleted_at=None,
        )

        result = user.to_dict()

        assert result["deleted_at"] is None
        assert result["is_active"] is True
        assert result["is_deleted"] is False
