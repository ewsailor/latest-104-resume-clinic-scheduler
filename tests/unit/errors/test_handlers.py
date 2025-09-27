"""
錯誤處理器測試模組。

測試錯誤處理輔助函式的獨特功能，專注於工廠函數和業務邏輯。
"""

# ===== 標準函式庫 =====
from datetime import date, time

# ===== 本地模組 =====
from app.errors.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    DatabaseError,
    ScheduleNotFoundError,
    ScheduleOverlapError,
    ServiceUnavailableError,
    UserNotFoundError,
    ValidationError,
)
from app.errors.handlers import (
    create_authentication_error,
    create_authorization_error,
    create_business_logic_error,
    create_conflict_error,
    create_database_error,
    create_schedule_cannot_be_deleted_error,
    create_schedule_not_found_error,
    create_schedule_overlap_error,
    create_service_unavailable_error,
    create_user_not_found_error,
    create_validation_error,
)
from app.errors.handlers import get_deletion_explanation  # 解釋刪除時段的原因


class TestErrorHandlerConsistency:
    """錯誤處理器一致性測試。"""

    def test_all_handlers_return_correct_types(self):
        """測試所有處理器回傳正確的錯誤類型。"""
        # 測試所有處理器函數
        handlers = [
            (create_validation_error, ValidationError, "驗證錯誤"),
            (create_authentication_error, AuthenticationError, "認證錯誤"),
            (create_authorization_error, AuthorizationError, "權限錯誤"),
            (create_business_logic_error, BusinessLogicError, "業務邏輯錯誤"),
            (create_schedule_not_found_error, ScheduleNotFoundError, 123),
            (create_user_not_found_error, UserNotFoundError, 456),
            (
                create_schedule_overlap_error,
                ScheduleOverlapError,
                "檢測到 1 個重疊時段，請調整時段之時間",
            ),
            (create_database_error, DatabaseError, "資料庫錯誤"),
            (create_service_unavailable_error, ServiceUnavailableError, "服務不可用"),
        ]

        for handler_func, expected_type, arg in handlers:
            error = handler_func(arg)
            assert isinstance(error, expected_type)
            assert isinstance(error, Exception)

    def test_error_handlers_message_format(self):
        """測試錯誤處理器訊息格式。"""
        # 測試 ID 相關的錯誤處理器
        id_handlers = [
            (create_schedule_not_found_error, "時段不存在: ID=123"),
            (create_user_not_found_error, "使用者不存在: ID=456"),
            (create_schedule_overlap_error, "檢測到 1 個重疊時段，請調整時段之時間"),
        ]

        for handler_func, expected_message in id_handlers:
            if handler_func == create_schedule_overlap_error:
                error = handler_func(expected_message)
            else:
                error = handler_func(
                    123
                    if "123" in expected_message
                    else 456 if "456" in expected_message else 789
                )
            assert error.message == expected_message

    def test_error_handlers_status_codes(self):
        """測試錯誤處理器狀態碼。"""
        # 測試各種錯誤的狀態碼
        status_tests = [
            (create_validation_error("test"), 422),
            (create_authentication_error("test"), 401),
            (create_authorization_error("test"), 403),
            (create_business_logic_error("test"), 400),
            (create_schedule_not_found_error(1), 404),
            (create_user_not_found_error(1), 404),
            (
                create_schedule_overlap_error("檢測到 1 個重疊時段，請調整時段之時間"),
                409,
            ),
            (create_database_error("test"), 500),
            (create_service_unavailable_error("test"), 503),
        ]

        for error, expected_status in status_tests:
            assert error.status_code == expected_status

    def test_error_handlers_error_codes(self):
        """測試錯誤處理器錯誤代碼。"""
        # 測試各種錯誤的錯誤代碼
        code_tests = [
            (create_validation_error("test"), "ROUTER_VALIDATION_ERROR"),
            (create_authentication_error("test"), "ROUTER_AUTHENTICATION_ERROR"),
            (create_authorization_error("test"), "ROUTER_AUTHORIZATION_ERROR"),
            (create_business_logic_error("test"), "SERVICE_BUSINESS_LOGIC_ERROR"),
            (create_schedule_not_found_error(1), "SERVICE_SCHEDULE_NOT_FOUND"),
            (create_user_not_found_error(1), "SERVICE_USER_NOT_FOUND"),
            (
                create_schedule_overlap_error("檢測到 1 個重疊時段，請調整時段之時間"),
                "SERVICE_SCHEDULE_OVERLAP",
            ),
            (create_database_error("test"), "CRUD_DATABASE_ERROR"),
            (create_service_unavailable_error("test"), "SERVICE_UNAVAILABLE"),
        ]

        for error, expected_code in code_tests:
            assert error.error_code == expected_code


class TestGetDeletionExplanation:
    """get_deletion_explanation 函數測試。"""

    def test_get_deletion_explanation_accepted(self):
        """測試已接受狀態的解釋。"""
        explanation = get_deletion_explanation("ACCEPTED")
        expected = "已接受的時段無法刪除，因為雙方已確認面談時間，刪除會影響約定"
        assert explanation == expected

    def test_get_deletion_explanation_completed(self):
        """測試已完成狀態的解釋。"""
        explanation = get_deletion_explanation("COMPLETED")
        expected = "已完成的時段無法刪除，因為面談已完成，屬於歷史記錄，不應刪除"
        assert explanation == expected

    def test_get_deletion_explanation_cancelled(self):
        """測試已取消狀態的解釋。"""
        explanation = get_deletion_explanation("CANCELLED")
        expected = "時段狀態不允許刪除"
        assert explanation == expected

    def test_get_deletion_explanation_unknown_status(self):
        """測試未知狀態的解釋。"""
        explanation = get_deletion_explanation("UNKNOWN")
        expected = "時段狀態不允許刪除"
        assert explanation == expected

    def test_get_deletion_explanation_empty_string(self):
        """測試空字串狀態的解釋。"""
        explanation = get_deletion_explanation("")
        expected = "時段狀態不允許刪除"
        assert explanation == expected

    def test_get_deletion_explanation_none(self):
        """測試 None 狀態的解釋。"""
        explanation = get_deletion_explanation(None)
        expected = "時段狀態不允許刪除"
        assert explanation == expected

    def test_get_deletion_explanation_all_valid_statuses(self):
        """測試所有有效狀態的解釋。"""
        test_cases = [
            (
                "ACCEPTED",
                "已接受的時段無法刪除，因為雙方已確認面談時間，刪除會影響約定",
            ),
            (
                "COMPLETED",
                "已完成的時段無法刪除，因為面談已完成，屬於歷史記錄，不應刪除",
            ),
        ]

        for status, expected in test_cases:
            explanation = get_deletion_explanation(status)
            assert explanation == expected

    def test_get_deletion_explanation_invalid_statuses(self):
        """測試無效狀態的解釋。"""
        invalid_statuses = [
            "PENDING",
            "AVAILABLE",
            "DRAFT",
            "CANCELLED",  # 已取消的時段應該返回 404 錯誤，不是 409 錯誤
            "INVALID",
            "123",
            "test",
        ]

        for status in invalid_statuses:
            explanation = get_deletion_explanation(status)
            assert explanation == "時段狀態不允許刪除"

    def test_get_deletion_explanation_case_sensitivity(self):
        """測試大小寫敏感性。"""
        # 測試小寫
        explanation_lower = get_deletion_explanation("accepted")
        assert explanation_lower == "時段狀態不允許刪除"

        # 測試混合大小寫
        explanation_mixed = get_deletion_explanation("Accepted")
        assert explanation_mixed == "時段狀態不允許刪除"

        # 測試正確的大寫
        explanation_upper = get_deletion_explanation("ACCEPTED")
        expected = "已接受的時段無法刪除，因為雙方已確認面談時間，刪除會影響約定"
        assert explanation_upper == expected


class TestCreateScheduleCannotBeDeletedError:
    """create_schedule_cannot_be_deleted_error 函數測試。"""

    def test_create_schedule_cannot_be_deleted_error_basic(self):
        """測試基本的時段無法刪除錯誤建立。"""
        error = create_schedule_cannot_be_deleted_error(123)

        assert error.message == "時段無法刪除: ID=123"
        assert error.error_code == "SERVICE_SCHEDULE_CANNOT_BE_DELETED"
        assert error.status_code == 409
        assert error.details == {}

    def test_create_schedule_cannot_be_deleted_error_with_reason(self):
        """測試帶有原因的時段無法刪除錯誤建立。"""
        error = create_schedule_cannot_be_deleted_error(456, reason="狀態不允許刪除")

        assert error.message == "時段無法刪除: ID=456"
        assert error.error_code == "SERVICE_SCHEDULE_CANNOT_BE_DELETED"
        assert error.status_code == 409
        assert error.details == {"reason": "狀態不允許刪除"}

    def test_create_schedule_cannot_be_deleted_error_with_status(self):
        """測試帶有狀態的時段無法刪除錯誤建立。"""
        error = create_schedule_cannot_be_deleted_error(789, schedule_status="ACCEPTED")

        assert error.message == "時段無法刪除: ID=789"
        assert error.error_code == "SERVICE_SCHEDULE_CANNOT_BE_DELETED"
        assert error.status_code == 409
        assert error.details == {
            "current_status": "ACCEPTED",
            "explanation": "已接受的時段無法刪除，因為雙方已確認面談時間，刪除會影響約定",
        }

    def test_create_schedule_cannot_be_deleted_error_with_all_params(self):
        """測試帶有所有參數的時段無法刪除錯誤建立。"""
        error = create_schedule_cannot_be_deleted_error(
            999, reason="狀態不允許刪除", schedule_status="COMPLETED"
        )

        assert error.message == "時段無法刪除: ID=999"
        assert error.error_code == "SERVICE_SCHEDULE_CANNOT_BE_DELETED"
        assert error.status_code == 409
        assert error.details == {
            "reason": "狀態不允許刪除",
            "current_status": "COMPLETED",
            "explanation": "已完成的時段無法刪除，因為面談已完成，屬於歷史記錄，不應刪除",
        }

    def test_create_schedule_cannot_be_deleted_error_string_id(self):
        """測試字串 ID 的時段無法刪除錯誤建立。"""
        error = create_schedule_cannot_be_deleted_error("test_id")

        assert error.message == "時段無法刪除: ID=test_id"
        assert error.error_code == "SERVICE_SCHEDULE_CANNOT_BE_DELETED"
        assert error.status_code == 409
        assert error.details == {}


class TestCreateScheduleOverlapError:
    """create_schedule_overlap_error 函數測試 - 專注於複雜的 details 處理。"""

    def test_create_schedule_overlap_error_with_overlapping_schedules(self):
        """測試帶有重疊時段詳細資訊的錯誤建立。"""

        # 模擬重疊時段物件
        class MockSchedule:
            def __init__(self, id, giver_id, date, start_time, end_time, status):
                self.id = id
                self.giver_id = giver_id
                self.date = date
                self.start_time = start_time
                self.end_time = end_time
                self.status = status

        # 建立模擬的日期時間物件
        # 模擬 ScheduleStatus 枚舉
        class MockScheduleStatus:
            def __init__(self, value):
                self.value = value

            ACCEPTED = "ACCEPTED"
            PENDING = "PENDING"

        mock_schedules = [
            MockSchedule(
                id=1,
                giver_id=100,
                date=date(2024, 1, 15),
                start_time=time(10, 0),
                end_time=time(11, 0),
                status=MockScheduleStatus("ACCEPTED"),
            ),
            MockSchedule(
                id=2,
                giver_id=200,
                date=date(2024, 1, 15),
                start_time=time(10, 30),
                end_time=time(11, 30),
                status=MockScheduleStatus("PENDING"),
            ),
        ]

        error = create_schedule_overlap_error(
            "檢測到 2 個重疊時段，請調整時段之時間",
            overlapping_schedules=mock_schedules,
        )

        assert error.message == "檢測到 2 個重疊時段，請調整時段之時間"
        assert error.error_code == "SERVICE_SCHEDULE_OVERLAP"
        assert error.status_code == 409

        # 驗證 details 中的重疊時段資訊
        assert "overlapping_schedules" in error.details
        overlapping_schedules = error.details["overlapping_schedules"]
        assert len(overlapping_schedules) == 2

        # 驗證第一個重疊時段的詳細資訊
        first_schedule = overlapping_schedules[0]
        assert first_schedule["id"] == 1
        assert first_schedule["giver_id"] == 100
        assert first_schedule["date"] == "2024-01-15"
        assert first_schedule["start_time"] == "10:00:00"
        assert first_schedule["end_time"] == "11:00:00"
        assert first_schedule["status"] == "ACCEPTED"

    def test_create_schedule_overlap_error_without_overlapping_schedules(self):
        """測試不帶重疊時段詳細資訊的錯誤建立。"""
        error = create_schedule_overlap_error("檢測到重疊時段")

        assert error.message == "檢測到重疊時段"
        assert error.error_code == "SERVICE_SCHEDULE_OVERLAP"
        assert error.status_code == 409
        assert error.details == {}

    def test_create_schedule_overlap_error_with_none_overlapping_schedules(self):
        """測試帶有 None 重疊時段的錯誤建立。"""
        error = create_schedule_overlap_error(
            "檢測到重疊時段", overlapping_schedules=None
        )

        assert error.message == "檢測到重疊時段"
        assert error.error_code == "SERVICE_SCHEDULE_OVERLAP"
        assert error.status_code == 409
        assert error.details == {}


class TestCreateConflictError:
    """create_conflict_error 函數測試 - 專注於 details 參數處理。"""

    def test_create_conflict_error_without_details(self):
        """測試不帶 details 的衝突錯誤建立。"""
        error = create_conflict_error("資源衝突")

        assert error.message == "資源衝突"
        assert error.error_code == "SERVICE_CONFLICT"
        assert error.status_code == 409
        assert error.details == {}

    def test_create_conflict_error_with_details(self):
        """測試帶有 details 的衝突錯誤建立。"""
        details = {
            "resource_type": "schedule",
            "conflicting_field": "time_slot",
            "existing_value": "10:00-11:00",
        }
        error = create_conflict_error("時段時間衝突", details=details)

        assert error.message == "時段時間衝突"
        assert error.error_code == "SERVICE_CONFLICT"
        assert error.status_code == 409
        assert error.details == details

    def test_create_conflict_error_with_none_details(self):
        """測試帶有 None details 的衝突錯誤建立。"""
        error = create_conflict_error("資源衝突", details=None)

        assert error.message == "資源衝突"
        assert error.error_code == "SERVICE_CONFLICT"
        assert error.status_code == 409
        assert error.details == {}
