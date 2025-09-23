"""
User 模型單元測試。

測試 User 模型的基本屬性、方法和業務邏輯。
專注於單一模型的功能，不涉及資料庫關係。
"""

# ===== 標準函式庫 =====
from datetime import datetime

# ===== 本地模組 =====
from app.models.user import User

# ===== 第三方套件 =====


class TestUserModel:
    """User 模型單元測試類別。"""

    def test_user_creation(self):
        """測試 User 實例創建。"""
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        # 測試基本屬性
        assert user.name == "測試使用者"
        assert user.email == "test@example.com"
        assert user.deleted_at is None

    def test_user_default_values(self):
        """測試 User 預設值。"""
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        # 測試預設值
        assert user.deleted_at is None

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

    def test_user_validation(self):
        """測試使用者資料驗證。"""
        # 測試有效資料
        user = User(
            name="測試使用者",
            email="test@example.com",
        )
        assert user.name == "測試使用者"
        assert user.email == "test@example.com"

    def test_user_repr(self):
        """測試 User 字串表示。"""
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        repr_str = repr(user)
        assert "User" in repr_str
        assert "name='測試使用者'" in repr_str
        assert "email='test@example.com'" in repr_str

    def test_user_to_dict(self):
        """測試 User to_dict 方法。"""
        user = User(
            name="測試使用者",
            email="test@example.com",
        )

        result = user.to_dict()

        assert isinstance(result, dict)
        assert result["name"] == "測試使用者"
        assert result["email"] == "test@example.com"
        assert result["is_active"] is True
        assert result["is_deleted"] is False

    def test_user_soft_delete(self):
        """測試使用者軟刪除。"""
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

        # 恢復
        user.deleted_at = None
        assert user.is_active is True
        assert user.is_deleted is False
