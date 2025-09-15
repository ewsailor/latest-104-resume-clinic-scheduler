"""
操作相關枚舉測試模組。

測試 OperationContext、ValidationContext 和 AuditAction 的功能。
"""

# ===== 標準函式庫 =====
from enum import Enum

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.enums.operations import AuditAction, OperationContext, ValidationContext


class TestOperationContext:
    """OperationContext 測試類別。"""

    def test_operation_context_enum_values(self):
        """測試 OperationContext 的值。"""
        assert OperationContext.CREATE == "建立"
        assert OperationContext.UPDATE == "更新"
        assert OperationContext.DELETE == "刪除"
        assert OperationContext.DUPLICATE == "複製"
        assert OperationContext.ARCHIVE == "封存"

    def test_operation_context_enum_membership(self):
        """測試 OperationContext 成員資格。"""
        valid_operations = ["建立", "更新", "刪除", "複製", "封存"]
        for operation in valid_operations:
            assert operation in OperationContext

        assert "無效操作" not in OperationContext

    def test_operation_context_enum_iteration(self):
        """測試 OperationContext 迭代。"""
        operations = list(OperationContext)
        assert len(operations) == 5
        expected_operations = [
            OperationContext.CREATE,
            OperationContext.UPDATE,
            OperationContext.DELETE,
            OperationContext.DUPLICATE,
            OperationContext.ARCHIVE,
        ]
        for expected in expected_operations:
            assert expected in operations

    def test_operation_context_enum_string_behavior(self):
        """測試 OperationContext 字串行為。"""
        # 測試字串比較
        assert str(OperationContext.CREATE) == "OperationContext.CREATE"
        assert OperationContext.UPDATE == "更新"
        assert OperationContext.DELETE == "刪除"  # 這裡應該是相等的

    def test_operation_context_enum_from_string(self):
        """測試從字串創建 OperationContext。"""
        assert OperationContext("建立") == OperationContext.CREATE
        assert OperationContext("更新") == OperationContext.UPDATE
        assert OperationContext("刪除") == OperationContext.DELETE
        assert OperationContext("複製") == OperationContext.DUPLICATE
        assert OperationContext("封存") == OperationContext.ARCHIVE

    def test_operation_context_enum_invalid_value(self):
        """測試無效值。"""
        with pytest.raises(ValueError):
            OperationContext("無效操作")

    def test_operation_context_enum_name_property(self):
        """測試 OperationContext 的 name 屬性。"""
        assert OperationContext.CREATE.name == "CREATE"
        assert OperationContext.UPDATE.name == "UPDATE"
        assert OperationContext.DELETE.name == "DELETE"
        assert OperationContext.DUPLICATE.name == "DUPLICATE"
        assert OperationContext.ARCHIVE.name == "ARCHIVE"

    def test_operation_context_enum_value_property(self):
        """測試 OperationContext 的 value 屬性。"""
        assert OperationContext.CREATE.value == "建立"
        assert OperationContext.UPDATE.value == "更新"
        assert OperationContext.DELETE.value == "刪除"
        assert OperationContext.DUPLICATE.value == "複製"
        assert OperationContext.ARCHIVE.value == "封存"

    def test_operation_context_enum_equality(self):
        """測試 OperationContext 相等性比較。"""
        assert OperationContext.CREATE == OperationContext.CREATE
        assert OperationContext.CREATE != OperationContext.UPDATE
        assert OperationContext.UPDATE == "更新"
        assert OperationContext.DELETE != "建立"

    def test_operation_context_enum_hash(self):
        """測試 OperationContext 可哈希性。"""
        # 測試可以作為字典鍵
        operation_dict = {
            OperationContext.CREATE: "create",
            OperationContext.UPDATE: "update",
            OperationContext.DELETE: "delete",
            OperationContext.DUPLICATE: "duplicate",
            OperationContext.ARCHIVE: "archive",
        }
        assert operation_dict[OperationContext.CREATE] == "create"
        assert operation_dict[OperationContext.UPDATE] == "update"
        assert operation_dict[OperationContext.DELETE] == "delete"

    def test_operation_context_enum_inheritance(self):
        """測試 OperationContext 繼承行為。"""
        # 測試繼承自 str 和 Enum
        assert isinstance(OperationContext.CREATE, str)
        assert isinstance(OperationContext.CREATE, OperationContext)
        assert isinstance(OperationContext.CREATE, Enum)

    def test_operation_context_enum_all_members(self):
        """測試 OperationContext 所有成員。"""
        all_operations = [op.value for op in OperationContext]
        expected_operations = ["建立", "更新", "刪除", "複製", "封存"]
        assert set(all_operations) == set(expected_operations)

    def test_operation_context_enum_crud_operations(self):
        """測試 CRUD 操作。"""
        # 基本 CRUD 操作
        crud_operations = [
            OperationContext.CREATE,
            OperationContext.UPDATE,
            OperationContext.DELETE,
        ]
        for operation in crud_operations:
            assert operation in OperationContext

    def test_operation_context_enum_extended_operations(self):
        """測試擴展操作。"""
        # 擴展操作
        extended_operations = [
            OperationContext.DUPLICATE,
            OperationContext.ARCHIVE,
        ]
        for operation in extended_operations:
            assert operation in OperationContext


class TestValidationContext:
    """ValidationContext 測試類別。"""

    def test_validation_context_enum_values(self):
        """測試 ValidationContext 的值。"""
        assert ValidationContext.PRE_SAVE == "儲存前"
        assert ValidationContext.POST_SAVE == "儲存後"
        assert ValidationContext.PRE_DELETE == "刪除前"
        assert ValidationContext.PRE_UPDATE == "更新前"

    def test_validation_context_enum_membership(self):
        """測試 ValidationContext 成員資格。"""
        valid_contexts = ["儲存前", "儲存後", "刪除前", "更新前"]
        for context in valid_contexts:
            assert context in ValidationContext

        assert "無效上下文" not in ValidationContext

    def test_validation_context_enum_iteration(self):
        """測試 ValidationContext 迭代。"""
        contexts = list(ValidationContext)
        assert len(contexts) == 4
        expected_contexts = [
            ValidationContext.PRE_SAVE,
            ValidationContext.POST_SAVE,
            ValidationContext.PRE_DELETE,
            ValidationContext.PRE_UPDATE,
        ]
        for expected in expected_contexts:
            assert expected in contexts

    def test_validation_context_enum_string_behavior(self):
        """測試 ValidationContext 字串行為。"""
        # 測試字串比較
        assert str(ValidationContext.PRE_SAVE) == "ValidationContext.PRE_SAVE"
        assert ValidationContext.POST_SAVE == "儲存後"
        assert ValidationContext.PRE_DELETE != "刪除後"  # 不存在

    def test_validation_context_enum_from_string(self):
        """測試從字串創建 ValidationContext。"""
        assert ValidationContext("儲存前") == ValidationContext.PRE_SAVE
        assert ValidationContext("儲存後") == ValidationContext.POST_SAVE
        assert ValidationContext("刪除前") == ValidationContext.PRE_DELETE
        assert ValidationContext("更新前") == ValidationContext.PRE_UPDATE

    def test_validation_context_enum_invalid_value(self):
        """測試無效值。"""
        with pytest.raises(ValueError):
            ValidationContext("無效上下文")

    def test_validation_context_enum_name_property(self):
        """測試 ValidationContext 的 name 屬性。"""
        assert ValidationContext.PRE_SAVE.name == "PRE_SAVE"
        assert ValidationContext.POST_SAVE.name == "POST_SAVE"
        assert ValidationContext.PRE_DELETE.name == "PRE_DELETE"
        assert ValidationContext.PRE_UPDATE.name == "PRE_UPDATE"

    def test_validation_context_enum_value_property(self):
        """測試 ValidationContext 的 value 屬性。"""
        assert ValidationContext.PRE_SAVE.value == "儲存前"
        assert ValidationContext.POST_SAVE.value == "儲存後"
        assert ValidationContext.PRE_DELETE.value == "刪除前"
        assert ValidationContext.PRE_UPDATE.value == "更新前"

    def test_validation_context_enum_equality(self):
        """測試 ValidationContext 相等性比較。"""
        assert ValidationContext.PRE_SAVE == ValidationContext.PRE_SAVE
        assert ValidationContext.PRE_SAVE != ValidationContext.POST_SAVE
        assert ValidationContext.PRE_SAVE == "儲存前"
        assert ValidationContext.POST_SAVE != "儲存前"

    def test_validation_context_enum_hash(self):
        """測試 ValidationContext 可哈希性。"""
        # 測試可以作為字典鍵
        context_dict = {
            ValidationContext.PRE_SAVE: "pre_save",
            ValidationContext.POST_SAVE: "post_save",
            ValidationContext.PRE_DELETE: "pre_delete",
            ValidationContext.PRE_UPDATE: "pre_update",
        }
        assert context_dict[ValidationContext.PRE_SAVE] == "pre_save"
        assert context_dict[ValidationContext.POST_SAVE] == "post_save"
        assert context_dict[ValidationContext.PRE_DELETE] == "pre_delete"

    def test_validation_context_enum_inheritance(self):
        """測試 ValidationContext 繼承行為。"""
        # 測試繼承自 str 和 Enum
        assert isinstance(ValidationContext.PRE_SAVE, str)
        assert isinstance(ValidationContext.PRE_SAVE, ValidationContext)
        assert isinstance(ValidationContext.PRE_SAVE, Enum)

    def test_validation_context_enum_all_members(self):
        """測試 ValidationContext 所有成員。"""
        all_contexts = [ctx.value for ctx in ValidationContext]
        expected_contexts = ["儲存前", "儲存後", "刪除前", "更新前"]
        assert set(all_contexts) == set(expected_contexts)

    def test_validation_context_enum_pre_operations(self):
        """測試前置操作驗證。"""
        pre_operations = [
            ValidationContext.PRE_SAVE,
            ValidationContext.PRE_DELETE,
            ValidationContext.PRE_UPDATE,
        ]
        for context in pre_operations:
            assert context in ValidationContext
            assert (
                context.value.startswith("儲存前")
                or context.value.startswith("刪除前")
                or context.value.startswith("更新前")
            )

    def test_validation_context_enum_post_operations(self):
        """測試後置操作驗證。"""
        post_operations = [ValidationContext.POST_SAVE]
        for context in post_operations:
            assert context in ValidationContext
            assert context.value.startswith("儲存後")


class TestAuditAction:
    """AuditAction 測試類別。"""

    def test_audit_action_enum_values(self):
        """測試 AuditAction 的值。"""
        assert AuditAction.CREATE == "建立"
        assert AuditAction.UPDATE == "更新"
        assert AuditAction.DELETE == "刪除"
        assert AuditAction.VIEW == "查看"
        assert AuditAction.EXPORT == "匯出"

    def test_audit_action_enum_membership(self):
        """測試 AuditAction 成員資格。"""
        valid_actions = ["建立", "更新", "刪除", "查看", "匯出"]
        for action in valid_actions:
            assert action in AuditAction

        assert "無效操作" not in AuditAction

    def test_audit_action_enum_iteration(self):
        """測試 AuditAction 迭代。"""
        actions = list(AuditAction)
        assert len(actions) == 5
        expected_actions = [
            AuditAction.CREATE,
            AuditAction.UPDATE,
            AuditAction.DELETE,
            AuditAction.VIEW,
            AuditAction.EXPORT,
        ]
        for expected in expected_actions:
            assert expected in actions

    def test_audit_action_enum_string_behavior(self):
        """測試 AuditAction 字串行為。"""
        # 測試字串比較
        assert str(AuditAction.CREATE) == "AuditAction.CREATE"
        assert AuditAction.UPDATE == "更新"
        assert AuditAction.VIEW != "瀏覽"  # 不同的詞

    def test_audit_action_enum_from_string(self):
        """測試從字串創建 AuditAction。"""
        assert AuditAction("建立") == AuditAction.CREATE
        assert AuditAction("更新") == AuditAction.UPDATE
        assert AuditAction("刪除") == AuditAction.DELETE
        assert AuditAction("查看") == AuditAction.VIEW
        assert AuditAction("匯出") == AuditAction.EXPORT

    def test_audit_action_enum_invalid_value(self):
        """測試無效值。"""
        with pytest.raises(ValueError):
            AuditAction("無效操作")

    def test_audit_action_enum_name_property(self):
        """測試 AuditAction 的 name 屬性。"""
        assert AuditAction.CREATE.name == "CREATE"
        assert AuditAction.UPDATE.name == "UPDATE"
        assert AuditAction.DELETE.name == "DELETE"
        assert AuditAction.VIEW.name == "VIEW"
        assert AuditAction.EXPORT.name == "EXPORT"

    def test_audit_action_enum_value_property(self):
        """測試 AuditAction 的 value 屬性。"""
        assert AuditAction.CREATE.value == "建立"
        assert AuditAction.UPDATE.value == "更新"
        assert AuditAction.DELETE.value == "刪除"
        assert AuditAction.VIEW.value == "查看"
        assert AuditAction.EXPORT.value == "匯出"

    def test_audit_action_enum_equality(self):
        """測試 AuditAction 相等性比較。"""
        assert AuditAction.CREATE == AuditAction.CREATE
        assert AuditAction.CREATE != AuditAction.UPDATE
        assert AuditAction.VIEW == "查看"
        assert AuditAction.EXPORT != "建立"

    def test_audit_action_enum_hash(self):
        """測試 AuditAction 可哈希性。"""
        # 測試可以作為字典鍵
        action_dict = {
            AuditAction.CREATE: "create",
            AuditAction.UPDATE: "update",
            AuditAction.DELETE: "delete",
            AuditAction.VIEW: "view",
            AuditAction.EXPORT: "export",
        }
        assert action_dict[AuditAction.CREATE] == "create"
        assert action_dict[AuditAction.UPDATE] == "update"
        assert action_dict[AuditAction.VIEW] == "view"

    def test_audit_action_enum_inheritance(self):
        """測試 AuditAction 繼承行為。"""
        # 測試繼承自 str 和 Enum
        assert isinstance(AuditAction.CREATE, str)
        assert isinstance(AuditAction.CREATE, AuditAction)
        assert isinstance(AuditAction.CREATE, Enum)

    def test_audit_action_enum_all_members(self):
        """測試 AuditAction 所有成員。"""
        all_actions = [action.value for action in AuditAction]
        expected_actions = ["建立", "更新", "刪除", "查看", "匯出"]
        assert set(all_actions) == set(expected_actions)

    def test_audit_action_enum_crud_actions(self):
        """測試 CRUD 審計操作。"""
        # 基本 CRUD 操作
        crud_actions = [
            AuditAction.CREATE,
            AuditAction.UPDATE,
            AuditAction.DELETE,
        ]
        for action in crud_actions:
            assert action in AuditAction

    def test_audit_action_enum_read_actions(self):
        """測試讀取相關審計操作。"""
        # 讀取相關操作
        read_actions = [AuditAction.VIEW, AuditAction.EXPORT]
        for action in read_actions:
            assert action in AuditAction

    def test_audit_action_enum_audit_categories(self):
        """測試審計操作分類。"""
        # 寫入操作
        write_actions = [AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE]
        for action in write_actions:
            assert action in AuditAction

        # 讀取操作
        read_actions = [AuditAction.VIEW, AuditAction.EXPORT]
        for action in read_actions:
            assert action in AuditAction
