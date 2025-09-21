"""
錯誤處理器測試模組。

測試錯誤處理輔助函式。
"""

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
    create_database_error,
    create_schedule_cannot_be_deleted_error,
    create_schedule_not_found_error,
    create_schedule_overlap_error,
    create_service_unavailable_error,
    create_user_not_found_error,
    create_validation_error,
    get_deletion_explanation,
)


class TestCreateValidationError:
    """create_validation_error 函數測試。"""

    def test_create_validation_error(self):
        """測試建立驗證錯誤。"""
        error = create_validation_error("驗證失敗")

        assert isinstance(error, ValidationError)
        assert error.message == "驗證失敗"
        assert error.error_code == "ROUTER_VALIDATION_ERROR"
        assert error.status_code == 422

    def test_create_validation_error_with_empty_message(self):
        """測試建立空訊息的驗證錯誤。"""
        error = create_validation_error("")

        assert isinstance(error, ValidationError)
        assert error.message == ""

    def test_create_validation_error_with_long_message(self):
        """測試建立長訊息的驗證錯誤。"""
        long_message = "這是一個非常長的驗證錯誤訊息，用來測試系統是否能正確處理長字串"
        error = create_validation_error(long_message)

        assert isinstance(error, ValidationError)
        assert error.message == long_message


class TestCreateAuthenticationError:
    """create_authentication_error 函數測試。"""

    def test_create_authentication_error(self):
        """測試建立認證錯誤。"""
        error = create_authentication_error("認證失敗")

        assert isinstance(error, AuthenticationError)
        assert error.message == "認證失敗"
        assert error.error_code == "ROUTER_AUTHENTICATION_ERROR"
        assert error.status_code == 401

    def test_create_authentication_error_with_default_message(self):
        """測試建立預設訊息的認證錯誤。"""
        error = create_authentication_error("認證失敗")

        assert isinstance(error, AuthenticationError)
        assert error.message == "認證失敗"


class TestCreateAuthorizationError:
    """create_authorization_error 函數測試。"""

    def test_create_authorization_error(self):
        """測試建立權限錯誤。"""
        error = create_authorization_error("權限不足")

        assert isinstance(error, AuthorizationError)
        assert error.message == "權限不足"
        assert error.error_code == "ROUTER_AUTHORIZATION_ERROR"
        assert error.status_code == 403

    def test_create_authorization_error_with_custom_message(self):
        """測試建立自定義訊息的權限錯誤。"""
        error = create_authorization_error("您沒有權限執行此操作")

        assert isinstance(error, AuthorizationError)
        assert error.message == "您沒有權限執行此操作"


class TestCreateBusinessLogicError:
    """create_business_logic_error 函數測試。"""

    def test_create_business_logic_error(self):
        """測試建立業務邏輯錯誤。"""
        error = create_business_logic_error("業務邏輯錯誤")

        assert isinstance(error, BusinessLogicError)
        assert error.message == "業務邏輯錯誤"
        assert error.error_code == "SERVICE_BUSINESS_LOGIC_ERROR"
        assert error.status_code == 400

    def test_create_business_logic_error_with_detailed_message(self):
        """測試建立詳細訊息的業務邏輯錯誤。"""
        message = "無法建立時段：時間衝突"
        error = create_business_logic_error(message)

        assert isinstance(error, BusinessLogicError)
        assert error.message == message


class TestCreateScheduleNotFoundError:
    """create_schedule_not_found_error 函數測試。"""

    def test_create_schedule_not_found_error_with_int_id(self):
        """測試建立整數 ID 的時段不存在錯誤。"""
        error = create_schedule_not_found_error(123)

        assert isinstance(error, ScheduleNotFoundError)
        assert error.message == "時段不存在: ID=123"
        assert error.error_code == "SERVICE_SCHEDULE_NOT_FOUND"
        assert error.status_code == 404

    def test_create_schedule_not_found_error_with_str_id(self):
        """測試建立字串 ID 的時段不存在錯誤。"""
        error = create_schedule_not_found_error("abc123")

        assert isinstance(error, ScheduleNotFoundError)
        assert error.message == "時段不存在: ID=abc123"
        assert error.error_code == "SERVICE_SCHEDULE_NOT_FOUND"
        assert error.status_code == 404

    def test_create_schedule_not_found_error_with_zero_id(self):
        """測試建立零 ID 的時段不存在錯誤。"""
        error = create_schedule_not_found_error(0)

        assert isinstance(error, ScheduleNotFoundError)
        assert error.message == "時段不存在: ID=0"

    def test_create_schedule_not_found_error_with_negative_id(self):
        """測試建立負數 ID 的時段不存在錯誤。"""
        error = create_schedule_not_found_error(-1)

        assert isinstance(error, ScheduleNotFoundError)
        assert error.message == "時段不存在: ID=-1"


class TestCreateUserNotFoundError:
    """create_user_not_found_error 函數測試。"""

    def test_create_user_not_found_error_with_int_id(self):
        """測試建立整數 ID 的使用者不存在錯誤。"""
        error = create_user_not_found_error(456)

        assert isinstance(error, UserNotFoundError)
        assert error.message == "使用者不存在: ID=456"
        assert error.error_code == "SERVICE_USER_NOT_FOUND"
        assert error.status_code == 404

    def test_create_user_not_found_error_with_str_id(self):
        """測試建立字串 ID 的使用者不存在錯誤。"""
        error = create_user_not_found_error("user123")

        assert isinstance(error, UserNotFoundError)
        assert error.message == "使用者不存在: ID=user123"
        assert error.error_code == "SERVICE_USER_NOT_FOUND"
        assert error.status_code == 404

    def test_create_user_not_found_error_with_email(self):
        """測試建立 email 的使用者不存在錯誤。"""
        error = create_user_not_found_error("test@example.com")

        assert isinstance(error, UserNotFoundError)
        assert error.message == "使用者不存在: ID=test@example.com"


class TestCreateScheduleOverlapError:
    """create_schedule_overlap_error 函數測試。"""

    def test_create_schedule_overlap_error_with_int_id(self):
        """測試建立整數 ID 的時段重疊錯誤。"""
        error = create_schedule_overlap_error("檢測到 1 個重疊時段，請調整時段之時間")

        assert isinstance(error, ScheduleOverlapError)
        assert error.message == "檢測到 1 個重疊時段，請調整時段之時間"
        assert error.error_code == "SERVICE_SCHEDULE_OVERLAP"
        assert error.status_code == 409

    def test_create_schedule_overlap_error_with_str_id(self):
        """測試建立字串 ID 的時段重疊錯誤。"""
        error = create_schedule_overlap_error(
            "更新時段 abc123 時，檢測到 1 個重疊時段，請調整時段之時間"
        )

        assert isinstance(error, ScheduleOverlapError)
        assert (
            error.message == "更新時段 abc123 時，檢測到 1 個重疊時段，請調整時段之時間"
        )
        assert error.error_code == "SERVICE_SCHEDULE_OVERLAP"
        assert error.status_code == 409


class TestCreateDatabaseError:
    """create_database_error 函數測試。"""

    def test_create_database_error(self):
        """測試建立資料庫錯誤。"""
        error = create_database_error("資料庫連線失敗")

        assert isinstance(error, DatabaseError)
        assert error.message == "資料庫連線失敗"
        assert error.error_code == "CRUD_DATABASE_ERROR"
        assert error.status_code == 500

    def test_create_database_error_with_sql_error(self):
        """測試建立 SQL 錯誤的資料庫錯誤。"""
        message = "SQL 語法錯誤: syntax error near 'SELECT'"
        error = create_database_error(message)

        assert isinstance(error, DatabaseError)
        assert error.message == message


class TestCreateServiceUnavailableError:
    """create_service_unavailable_error 函數測試。"""

    def test_create_service_unavailable_error(self):
        """測試建立服務不可用錯誤。"""
        error = create_service_unavailable_error("服務維護中")

        assert isinstance(error, ServiceUnavailableError)
        assert error.message == "服務維護中"
        assert error.error_code == "SERVICE_UNAVAILABLE"
        assert error.status_code == 503

    def test_create_service_unavailable_error_with_maintenance_message(self):
        """測試建立維護訊息的服務不可用錯誤。"""
        message = "系統維護中，預計 2 小時後恢復"
        error = create_service_unavailable_error(message)

        assert isinstance(error, ServiceUnavailableError)
        assert error.message == message


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
