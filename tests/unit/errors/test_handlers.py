"""
錯誤處理器測試模組。

測試錯誤處理輔助函式。
"""

# ===== 標準函式庫 =====

# ===== 本地模組 =====
from app.errors.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    LivenessCheckError,
    ReadinessCheckError,
    ScheduleNotFoundError,
    ServiceUnavailableError,
    UserNotFoundError,
    ValidationError,
)
from app.errors.handlers import (
    create_authentication_error,
    create_authorization_error,
    create_business_logic_error,
    create_database_error,
    create_liveness_check_error,
    create_readiness_check_error,
    create_schedule_not_found_error,
    create_schedule_overlap_error,
    create_service_unavailable_error,
    create_user_not_found_error,
    create_validation_error,
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
        error = create_schedule_overlap_error(123)

        assert isinstance(error, ConflictError)
        assert error.message == "時段重疊: ID=123"
        assert error.error_code == "SERVICE_CONFLICT"
        assert error.status_code == 409

    def test_create_schedule_overlap_error_with_str_id(self):
        """測試建立字串 ID 的時段重疊錯誤。"""
        error = create_schedule_overlap_error("abc123")

        assert isinstance(error, ConflictError)
        assert error.message == "時段重疊: ID=abc123"
        assert error.error_code == "SERVICE_CONFLICT"
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


class TestCreateLivenessCheckError:
    """create_liveness_check_error 函數測試。"""

    def test_create_liveness_check_error(self):
        """測試建立存活檢查錯誤。"""
        error = create_liveness_check_error("資料庫連線失敗")

        assert isinstance(error, LivenessCheckError)
        assert error.message == "資料庫連線失敗"
        assert error.error_code == "LIVENESS_CHECK_ERROR"
        assert error.status_code == 500

    def test_create_liveness_check_error_with_detailed_message(self):
        """測試建立詳細訊息的存活檢查錯誤。"""
        message = "Redis 連線超時，無法完成存活檢查"
        error = create_liveness_check_error(message)

        assert isinstance(error, LivenessCheckError)
        assert error.message == message


class TestCreateReadinessCheckError:
    """create_readiness_check_error 函數測試。"""

    def test_create_readiness_check_error(self):
        """測試建立準備就緒檢查錯誤。"""
        error = create_readiness_check_error("外部服務不可用")

        assert isinstance(error, ReadinessCheckError)
        assert error.message == "外部服務不可用"
        assert error.error_code == "READINESS_CHECK_ERROR"
        assert error.status_code == 503

    def test_create_readiness_check_error_with_service_message(self):
        """測試建立服務訊息的準備就緒檢查錯誤。"""
        message = "第三方 API 服務回應超時"
        error = create_readiness_check_error(message)

        assert isinstance(error, ReadinessCheckError)
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
            (create_schedule_overlap_error, ConflictError, 789),
            (create_database_error, DatabaseError, "資料庫錯誤"),
            (create_service_unavailable_error, ServiceUnavailableError, "服務不可用"),
            (create_liveness_check_error, LivenessCheckError, "存活檢查失敗"),
            (create_readiness_check_error, ReadinessCheckError, "準備就緒檢查失敗"),
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
            (create_schedule_overlap_error, "時段重疊: ID=789"),
        ]

        for handler_func, expected_message in id_handlers:
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
            (create_schedule_overlap_error(1), 409),
            (create_database_error("test"), 500),
            (create_service_unavailable_error("test"), 503),
            (create_liveness_check_error("test"), 500),
            (create_readiness_check_error("test"), 503),
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
            (create_schedule_overlap_error(1), "SERVICE_CONFLICT"),
            (create_database_error("test"), "CRUD_DATABASE_ERROR"),
            (create_service_unavailable_error("test"), "SERVICE_UNAVAILABLE"),
            (create_liveness_check_error("test"), "LIVENESS_CHECK_ERROR"),
            (create_readiness_check_error("test"), "READINESS_CHECK_ERROR"),
        ]

        for error, expected_code in code_tests:
            assert error.error_code == expected_code
