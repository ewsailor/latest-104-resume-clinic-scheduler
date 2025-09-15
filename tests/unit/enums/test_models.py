"""
模型相關枚舉測試模組。

測試 UserRoleEnum 和 ScheduleStatusEnum 的功能。
"""

# ===== 標準函式庫 =====
from enum import Enum

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum


class TestUserRoleEnum:
    """UserRoleEnum 測試類別。"""

    def test_user_role_enum_values(self):
        """測試 UserRoleEnum 的值。"""
        assert UserRoleEnum.GIVER == "GIVER"
        assert UserRoleEnum.TAKER == "TAKER"
        assert UserRoleEnum.SYSTEM == "SYSTEM"

    def test_user_role_enum_membership(self):
        """測試 UserRoleEnum 成員資格。"""
        assert "GIVER" in UserRoleEnum
        assert "TAKER" in UserRoleEnum
        assert "SYSTEM" in UserRoleEnum
        assert "ADMIN" not in UserRoleEnum

    def test_user_role_enum_iteration(self):
        """測試 UserRoleEnum 迭代。"""
        roles = list(UserRoleEnum)
        assert len(roles) == 3
        assert UserRoleEnum.GIVER in roles
        assert UserRoleEnum.TAKER in roles
        assert UserRoleEnum.SYSTEM in roles

    def test_user_role_enum_string_behavior(self):
        """測試 UserRoleEnum 字串行為。"""
        # 測試字串比較
        assert str(UserRoleEnum.GIVER) == "UserRoleEnum.GIVER"
        assert UserRoleEnum.GIVER == "GIVER"
        assert UserRoleEnum.GIVER != "giver"  # 大小寫敏感

    def test_user_role_enum_from_string(self):
        """測試從字串創建 UserRoleEnum。"""
        assert UserRoleEnum("GIVER") == UserRoleEnum.GIVER
        assert UserRoleEnum("TAKER") == UserRoleEnum.TAKER
        assert UserRoleEnum("SYSTEM") == UserRoleEnum.SYSTEM

    def test_user_role_enum_invalid_value(self):
        """測試無效值。"""
        with pytest.raises(ValueError):
            UserRoleEnum("INVALID")

    def test_user_role_enum_name_property(self):
        """測試 UserRoleEnum 的 name 屬性。"""
        assert UserRoleEnum.GIVER.name == "GIVER"
        assert UserRoleEnum.TAKER.name == "TAKER"
        assert UserRoleEnum.SYSTEM.name == "SYSTEM"

    def test_user_role_enum_value_property(self):
        """測試 UserRoleEnum 的 value 屬性。"""
        assert UserRoleEnum.GIVER.value == "GIVER"
        assert UserRoleEnum.TAKER.value == "TAKER"
        assert UserRoleEnum.SYSTEM.value == "SYSTEM"

    def test_user_role_enum_equality(self):
        """測試 UserRoleEnum 相等性比較。"""
        assert UserRoleEnum.GIVER == UserRoleEnum.GIVER
        assert UserRoleEnum.GIVER != UserRoleEnum.TAKER
        assert UserRoleEnum.GIVER == "GIVER"
        assert UserRoleEnum.GIVER != "TAKER"

    def test_user_role_enum_hash(self):
        """測試 UserRoleEnum 可哈希性。"""
        # 測試可以作為字典鍵
        role_dict = {
            UserRoleEnum.GIVER: "給予者",
            UserRoleEnum.TAKER: "接受者",
            UserRoleEnum.SYSTEM: "系統",
        }
        assert role_dict[UserRoleEnum.GIVER] == "給予者"
        assert role_dict[UserRoleEnum.TAKER] == "接受者"
        assert role_dict[UserRoleEnum.SYSTEM] == "系統"

    def test_user_role_enum_inheritance(self):
        """測試 UserRoleEnum 繼承行為。"""
        # 測試繼承自 str 和 Enum
        assert isinstance(UserRoleEnum.GIVER, str)
        assert isinstance(UserRoleEnum.GIVER, UserRoleEnum)
        assert isinstance(UserRoleEnum.GIVER, Enum)

    def test_user_role_enum_all_members(self):
        """測試 UserRoleEnum 所有成員。"""
        all_roles = [role.value for role in UserRoleEnum]
        expected_roles = ["GIVER", "TAKER", "SYSTEM"]
        assert set(all_roles) == set(expected_roles)


class TestScheduleStatusEnum:
    """ScheduleStatusEnum 測試類別。"""

    def test_schedule_status_enum_values(self):
        """測試 ScheduleStatusEnum 的值。"""
        assert ScheduleStatusEnum.DRAFT == "DRAFT"
        assert ScheduleStatusEnum.AVAILABLE == "AVAILABLE"
        assert ScheduleStatusEnum.PENDING == "PENDING"
        assert ScheduleStatusEnum.ACCEPTED == "ACCEPTED"
        assert ScheduleStatusEnum.REJECTED == "REJECTED"
        assert ScheduleStatusEnum.CANCELLED == "CANCELLED"
        assert ScheduleStatusEnum.COMPLETED == "COMPLETED"

    def test_schedule_status_enum_membership(self):
        """測試 ScheduleStatusEnum 成員資格。"""
        valid_statuses = [
            "DRAFT",
            "AVAILABLE",
            "PENDING",
            "ACCEPTED",
            "REJECTED",
            "CANCELLED",
            "COMPLETED",
        ]
        for status in valid_statuses:
            assert status in ScheduleStatusEnum

        assert "INVALID" not in ScheduleStatusEnum

    def test_schedule_status_enum_iteration(self):
        """測試 ScheduleStatusEnum 迭代。"""
        statuses = list(ScheduleStatusEnum)
        assert len(statuses) == 7
        expected_statuses = [
            ScheduleStatusEnum.DRAFT,
            ScheduleStatusEnum.AVAILABLE,
            ScheduleStatusEnum.PENDING,
            ScheduleStatusEnum.ACCEPTED,
            ScheduleStatusEnum.REJECTED,
            ScheduleStatusEnum.CANCELLED,
            ScheduleStatusEnum.COMPLETED,
        ]
        for expected in expected_statuses:
            assert expected in statuses

    def test_schedule_status_enum_string_behavior(self):
        """測試 ScheduleStatusEnum 字串行為。"""
        # 測試字串比較
        assert str(ScheduleStatusEnum.DRAFT) == "ScheduleStatusEnum.DRAFT"
        assert ScheduleStatusEnum.AVAILABLE == "AVAILABLE"
        assert ScheduleStatusEnum.PENDING != "pending"  # 大小寫敏感

    def test_schedule_status_enum_from_string(self):
        """測試從字串創建 ScheduleStatusEnum。"""
        assert ScheduleStatusEnum("DRAFT") == ScheduleStatusEnum.DRAFT
        assert ScheduleStatusEnum("AVAILABLE") == ScheduleStatusEnum.AVAILABLE
        assert ScheduleStatusEnum("PENDING") == ScheduleStatusEnum.PENDING
        assert ScheduleStatusEnum("ACCEPTED") == ScheduleStatusEnum.ACCEPTED
        assert ScheduleStatusEnum("REJECTED") == ScheduleStatusEnum.REJECTED
        assert ScheduleStatusEnum("CANCELLED") == ScheduleStatusEnum.CANCELLED
        assert ScheduleStatusEnum("COMPLETED") == ScheduleStatusEnum.COMPLETED

    def test_schedule_status_enum_invalid_value(self):
        """測試無效值。"""
        with pytest.raises(ValueError):
            ScheduleStatusEnum("INVALID")

    def test_schedule_status_enum_name_property(self):
        """測試 ScheduleStatusEnum 的 name 屬性。"""
        assert ScheduleStatusEnum.DRAFT.name == "DRAFT"
        assert ScheduleStatusEnum.AVAILABLE.name == "AVAILABLE"
        assert ScheduleStatusEnum.PENDING.name == "PENDING"
        assert ScheduleStatusEnum.ACCEPTED.name == "ACCEPTED"
        assert ScheduleStatusEnum.REJECTED.name == "REJECTED"
        assert ScheduleStatusEnum.CANCELLED.name == "CANCELLED"
        assert ScheduleStatusEnum.COMPLETED.name == "COMPLETED"

    def test_schedule_status_enum_value_property(self):
        """測試 ScheduleStatusEnum 的 value 屬性。"""
        assert ScheduleStatusEnum.DRAFT.value == "DRAFT"
        assert ScheduleStatusEnum.AVAILABLE.value == "AVAILABLE"
        assert ScheduleStatusEnum.PENDING.value == "PENDING"
        assert ScheduleStatusEnum.ACCEPTED.value == "ACCEPTED"
        assert ScheduleStatusEnum.REJECTED.value == "REJECTED"
        assert ScheduleStatusEnum.CANCELLED.value == "CANCELLED"
        assert ScheduleStatusEnum.COMPLETED.value == "COMPLETED"

    def test_schedule_status_enum_equality(self):
        """測試 ScheduleStatusEnum 相等性比較。"""
        assert ScheduleStatusEnum.DRAFT == ScheduleStatusEnum.DRAFT
        assert ScheduleStatusEnum.DRAFT != ScheduleStatusEnum.AVAILABLE
        assert ScheduleStatusEnum.AVAILABLE == "AVAILABLE"
        assert ScheduleStatusEnum.PENDING != "DRAFT"

    def test_schedule_status_enum_hash(self):
        """測試 ScheduleStatusEnum 可哈希性。"""
        # 測試可以作為字典鍵
        status_dict = {
            ScheduleStatusEnum.DRAFT: "草稿",
            ScheduleStatusEnum.AVAILABLE: "可預約",
            ScheduleStatusEnum.PENDING: "待確認",
            ScheduleStatusEnum.ACCEPTED: "已接受",
            ScheduleStatusEnum.REJECTED: "已拒絕",
            ScheduleStatusEnum.CANCELLED: "已取消",
            ScheduleStatusEnum.COMPLETED: "已完成",
        }
        assert status_dict[ScheduleStatusEnum.DRAFT] == "草稿"
        assert status_dict[ScheduleStatusEnum.AVAILABLE] == "可預約"
        assert status_dict[ScheduleStatusEnum.PENDING] == "待確認"

    def test_schedule_status_enum_inheritance(self):
        """測試 ScheduleStatusEnum 繼承行為。"""
        # 測試繼承自 str 和 Enum
        assert isinstance(ScheduleStatusEnum.DRAFT, str)
        assert isinstance(ScheduleStatusEnum.DRAFT, ScheduleStatusEnum)
        assert isinstance(ScheduleStatusEnum.DRAFT, Enum)

    def test_schedule_status_enum_all_members(self):
        """測試 ScheduleStatusEnum 所有成員。"""
        all_statuses = [status.value for status in ScheduleStatusEnum]
        expected_statuses = [
            "DRAFT",
            "AVAILABLE",
            "PENDING",
            "ACCEPTED",
            "REJECTED",
            "CANCELLED",
            "COMPLETED",
        ]
        assert set(all_statuses) == set(expected_statuses)

    def test_schedule_status_enum_workflow_states(self):
        """測試時段狀態的工作流程。"""
        # 測試初始狀態
        initial_states = [ScheduleStatusEnum.DRAFT, ScheduleStatusEnum.AVAILABLE]
        for state in initial_states:
            assert state in ScheduleStatusEnum

        # 測試進行中狀態
        in_progress_states = [ScheduleStatusEnum.PENDING, ScheduleStatusEnum.ACCEPTED]
        for state in in_progress_states:
            assert state in ScheduleStatusEnum

        # 測試終止狀態
        terminal_states = [
            ScheduleStatusEnum.REJECTED,
            ScheduleStatusEnum.CANCELLED,
            ScheduleStatusEnum.COMPLETED,
        ]
        for state in terminal_states:
            assert state in ScheduleStatusEnum

    def test_schedule_status_enum_status_categories(self):
        """測試時段狀態分類。"""
        # 可預約狀態
        bookable_statuses = [ScheduleStatusEnum.AVAILABLE]
        for status in bookable_statuses:
            assert status in ScheduleStatusEnum

        # 不可預約狀態
        non_bookable_statuses = [
            ScheduleStatusEnum.DRAFT,
            ScheduleStatusEnum.PENDING,
            ScheduleStatusEnum.ACCEPTED,
            ScheduleStatusEnum.REJECTED,
            ScheduleStatusEnum.CANCELLED,
            ScheduleStatusEnum.COMPLETED,
        ]
        for status in non_bookable_statuses:
            assert status in ScheduleStatusEnum
