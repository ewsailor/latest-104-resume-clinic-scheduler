"""
異常類別測試模組。

測試各種自定義異常類別的功能。
"""

from fastapi import status

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.errors.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    ScheduleCannotBeDeletedError,
    ScheduleNotFoundError,
    ScheduleOverlapError,
    ServiceUnavailableError,
    UserNotFoundError,
    ValidationError,
)


# ===== 錯誤層級測試 =====
class TestErrorHierarchy:
    """錯誤層級測試。"""

    def test_error_inheritance_hierarchy(self):
        """測試錯誤繼承層級。"""
        # 所有自定義錯誤都應該繼承自 APIError
        errors = [
            BadRequestError("test"),
            ValidationError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            BusinessLogicError("test"),
            ScheduleNotFoundError(1),
            UserNotFoundError(1),
            ConflictError("test"),
            ScheduleCannotBeDeletedError(1),
            ScheduleOverlapError("test"),
            DatabaseError("test"),
            ServiceUnavailableError("test"),
        ]

        for error in errors:
            assert isinstance(error, APIError)
            assert isinstance(error, Exception)

    def test_error_status_codes(self):
        """測試錯誤狀態碼。"""
        # 測試各種錯誤的狀態碼
        assert BadRequestError("test").status_code == status.HTTP_400_BAD_REQUEST
        assert (
            ValidationError("test").status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        assert AuthenticationError("test").status_code == status.HTTP_401_UNAUTHORIZED
        assert AuthorizationError("test").status_code == status.HTTP_403_FORBIDDEN
        assert BusinessLogicError("test").status_code == status.HTTP_400_BAD_REQUEST
        assert ScheduleNotFoundError(1).status_code == status.HTTP_404_NOT_FOUND
        assert UserNotFoundError(1).status_code == status.HTTP_404_NOT_FOUND
        assert ConflictError("test").status_code == status.HTTP_409_CONFLICT
        assert ScheduleCannotBeDeletedError(1).status_code == status.HTTP_409_CONFLICT
        assert ScheduleOverlapError("test").status_code == status.HTTP_409_CONFLICT
        assert (
            DatabaseError("test").status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        assert (
            ServiceUnavailableError("test").status_code
            == status.HTTP_503_SERVICE_UNAVAILABLE
        )

    def test_error_codes_format(self):
        """測試錯誤代碼格式。"""
        # 測試錯誤代碼的格式一致性
        errors = [
            BadRequestError("test"),
            ValidationError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            BusinessLogicError("test"),
            ScheduleNotFoundError(1),
            UserNotFoundError(1),
            ConflictError("test"),
            ScheduleCannotBeDeletedError(1),
            ScheduleOverlapError("test"),
            DatabaseError("test"),
            ServiceUnavailableError("test"),
        ]

        for error in errors:
            # 錯誤代碼應該包含層級前綴
            assert "_" in error.error_code
            # 錯誤代碼應該是大寫
            assert error.error_code.isupper() or "_" in error.error_code


# ===== APIError 基礎類別測試 =====
class TestAPIError:
    """APIError 基礎類別測試。"""

    def test_api_error_inheritance(self):
        """測試 APIError 繼承關係。"""
        error = APIError("測試錯誤", "TEST_ERROR")

        # 確認 error 繼承自 APIError 實例，可被 except APIError 捕獲
        assert isinstance(error, APIError)
        # 確認 error 繼承自 Exception，可被 except Exception 捕獲
        assert isinstance(error, Exception)

    @pytest.mark.parametrize(
        "message,error_code,status_code,details,expected_details",
        [
            # 基本測試
            ("測試錯誤", "TEST_ERROR", status.HTTP_400_BAD_REQUEST, None, {}),
            # 邊界測試：空詳細資訊
            ("測試錯誤", "TEST_ERROR", status.HTTP_400_BAD_REQUEST, {}, {}),
            # 自定義狀態碼測試
            ("測試錯誤", "TEST_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR, None, {}),
            # 帶詳細資訊測試
            (
                "測試錯誤",
                "TEST_ERROR",
                status.HTTP_400_BAD_REQUEST,
                {"code": 123, "msg": "error"},
                {"code": 123, "msg": "error"},
            ),
        ],
    )
    def test_api_error_creation(
        self,
        message: str,
        error_code: str,
        status_code: int,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 APIError 建立功能。

        使用參數化測試來覆蓋各種建立場景。
        """
        # 建立錯誤實例
        error = APIError(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details,
        )

        # 資料完整性驗證
        assert error.message == message
        assert error.error_code == error_code
        assert error.status_code == status_code
        assert error.details == expected_details
        assert str(error) == message


# ===== CRUD 層級錯誤 =====
class TestDatabaseError:
    """DatabaseError 測試。"""

    def test_database_error_inheritance(self) -> None:
        """測試 DatabaseError 繼承關係。"""
        error = DatabaseError("測試錯誤")

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "CRUD_DATABASE_ERROR"
        assert error.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.parametrize(
        "message,details,expected_details",
        [
            # 基本測試
            ("資料庫操作失敗", None, {}),
            # 邊界測試：空詳細資訊
            ("資料庫連線超時", {}, {}),
            # 帶詳細資訊測試
            ("資料庫操作失敗", {"operation": "INSERT"}, {"operation": "INSERT"}),
        ],
    )
    def test_database_error_creation(
        self,
        message: str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 DatabaseError 建立功能。"""
        error = DatabaseError(message, details)

        assert error.message == message
        assert error.error_code == "CRUD_DATABASE_ERROR"
        assert error.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert error.details == expected_details
        assert str(error) == message


# ===== Router 層級錯誤 =====
class TestBadRequestError:
    """BadRequestError 測試。"""

    def test_bad_request_error_inheritance(self) -> None:
        """測試 BadRequestError 繼承關係。"""
        error = BadRequestError("測試錯誤")

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "ROUTER_BAD_REQUEST"
        assert error.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "message,details,expected_details",
        [
            # 基本測試
            ("請求格式錯誤", None, {}),
            # 邊界測試：空詳細資訊
            ("請求格式錯誤", {}, {}),
            # 帶詳細資訊測試
            (
                "請求格式錯誤",
                {"field": "request_body", "error": "格式不正確"},
                {"field": "request_body", "error": "格式不正確"},
            ),
        ],
    )
    def test_bad_request_error_creation(
        self,
        message: str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 BadRequestError 建立功能。"""
        error = BadRequestError(message, details)

        assert error.message == message
        assert error.error_code == "ROUTER_BAD_REQUEST"
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.details == expected_details
        assert str(error) == message


class TestAuthenticationError:
    """AuthenticationError 測試。"""

    def test_authentication_error_inheritance(self) -> None:
        """測試 AuthenticationError 繼承關係。"""
        error = AuthenticationError("測試錯誤")

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "ROUTER_AUTHENTICATION_ERROR"
        assert error.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "message,details,expected_details",
        [
            # 基本測試
            ("認證失敗", None, {}),
            # 邊界測試：空詳細資訊
            ("認證失敗", {}, {}),
            # 帶詳細資訊測試
            ("認證失敗", {"token": "invalid"}, {"token": "invalid"}),
        ],
    )
    def test_authentication_error_creation(
        self,
        message: str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 AuthenticationError 建立功能。"""
        error = AuthenticationError(message, details)

        assert error.message == message
        assert error.error_code == "ROUTER_AUTHENTICATION_ERROR"
        assert error.status_code == status.HTTP_401_UNAUTHORIZED
        assert error.details == expected_details
        assert str(error) == message


class TestAuthorizationError:
    """AuthorizationError 測試。"""

    def test_authorization_error_inheritance(self) -> None:
        """測試 AuthorizationError 繼承關係。"""
        error = AuthorizationError("測試錯誤")

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "ROUTER_AUTHORIZATION_ERROR"
        assert error.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "message,details,expected_details",
        [
            # 基本測試
            ("權限不足", None, {}),
            # 邊界測試：空詳細資訊
            ("權限不足", {}, {}),
            # 帶詳細資訊測試
            ("權限不足", {"resource": "admin"}, {"resource": "admin"}),
        ],
    )
    def test_authorization_error_creation(
        self,
        message: str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 AuthorizationError 建立功能。"""
        error = AuthorizationError(message, details)

        assert error.message == message
        assert error.error_code == "ROUTER_AUTHORIZATION_ERROR"
        assert error.status_code == status.HTTP_403_FORBIDDEN
        assert error.details == expected_details
        assert str(error) == message


class TestValidationError:
    """ValidationError 測試。"""

    def test_validation_error_inheritance(self) -> None:
        """測試 ValidationError 繼承關係。"""
        error = ValidationError("測試錯誤")

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "ROUTER_VALIDATION_ERROR"
        assert error.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "message,details,expected_details",
        [
            # 基本測試
            ("驗證失敗", None, {}),
            # 邊界測試：空詳細資訊
            ("驗證失敗", {}, {}),
            # 帶詳細資訊測試
            (
                "驗證失敗",
                {"field": "email", "error": "格式不正確"},
                {"field": "email", "error": "格式不正確"},
            ),
        ],
    )
    def test_validation_error_creation(
        self,
        message: str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 ValidationError 建立功能。"""
        error = ValidationError(message, details)

        assert error.message == message
        assert error.error_code == "ROUTER_VALIDATION_ERROR"
        assert error.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert error.details == expected_details
        assert str(error) == message


# ===== Service 層級錯誤 =====
class TestBusinessLogicError:
    """BusinessLogicError 測試。"""

    def test_business_logic_error_inheritance(self) -> None:
        """測試 BusinessLogicError 繼承關係。"""
        error = BusinessLogicError("測試錯誤")

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "SERVICE_BUSINESS_LOGIC_ERROR"
        assert error.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "message,details,expected_details",
        [
            # 基本測試
            ("業務邏輯錯誤", None, {}),
            # 邊界測試：空詳細資訊
            ("業務邏輯錯誤", {}, {}),
            # 帶詳細資訊測試
            (
                "業務邏輯錯誤",
                {"operation": "create", "reason": "conflict"},
                {"operation": "create", "reason": "conflict"},
            ),
        ],
    )
    def test_business_logic_error_creation(
        self,
        message: str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 BusinessLogicError 建立功能。"""
        error = BusinessLogicError(message, details)

        assert error.message == message
        assert error.error_code == "SERVICE_BUSINESS_LOGIC_ERROR"
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.details == expected_details
        assert str(error) == message


class TestScheduleNotFoundError:
    """ScheduleNotFoundError 測試。"""

    def test_schedule_not_found_error_inheritance(self) -> None:
        """測試 ScheduleNotFoundError 繼承關係。"""
        error = ScheduleNotFoundError(123)

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "SERVICE_SCHEDULE_NOT_FOUND"
        assert error.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "schedule_id,details,expected_details",
        [
            # 基本測試
            (123, None, {}),
            ("abc123", None, {}),
            # 邊界測試：空詳細資訊
            (123, {}, {}),
            # 帶詳細資訊測試
            (
                123,
                {"search_criteria": "date=2024-01-01"},
                {"search_criteria": "date=2024-01-01"},
            ),
        ],
    )
    def test_schedule_not_found_error_creation(
        self,
        schedule_id: int | str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 ScheduleNotFoundError 建立功能。"""
        error = ScheduleNotFoundError(schedule_id, details)

        assert error.message == f"時段不存在: ID={schedule_id}"
        assert error.error_code == "SERVICE_SCHEDULE_NOT_FOUND"
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert error.details == expected_details
        assert str(error) == f"時段不存在: ID={schedule_id}"


class TestUserNotFoundError:
    """UserNotFoundError 測試。"""

    def test_user_not_found_error_inheritance(self) -> None:
        """測試 UserNotFoundError 繼承關係。"""
        error = UserNotFoundError(456)

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "SERVICE_USER_NOT_FOUND"
        assert error.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "user_id,details,expected_details",
        [
            # 基本測試
            (456, None, {}),
            ("user123", None, {}),
            # 邊界測試：空詳細資訊
            (456, {}, {}),
            # 帶詳細資訊測試
            (456, {"email": "test@example.com"}, {"email": "test@example.com"}),
        ],
    )
    def test_user_not_found_error_creation(
        self,
        user_id: int | str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 UserNotFoundError 建立功能。"""
        error = UserNotFoundError(user_id, details)

        assert error.message == f"使用者不存在: ID={user_id}"
        assert error.error_code == "SERVICE_USER_NOT_FOUND"
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert error.details == expected_details
        assert str(error) == f"使用者不存在: ID={user_id}"


class TestConflictError:
    """ConflictError 測試。"""

    def test_conflict_error_inheritance(self) -> None:
        """測試 ConflictError 繼承關係。"""
        error = ConflictError("測試錯誤")

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "SERVICE_CONFLICT"
        assert error.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.parametrize(
        "message,details,expected_details",
        [
            # 基本測試
            ("資源衝突", None, {}),
            # 邊界測試：空詳細資訊
            ("資源衝突", {}, {}),
            # 帶詳細資訊測試
            (
                "資源衝突",
                {"conflicting_field": "email", "existing_value": "test@example.com"},
                {"conflicting_field": "email", "existing_value": "test@example.com"},
            ),
        ],
    )
    def test_conflict_error_creation(
        self,
        message: str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 ConflictError 建立功能。"""
        error = ConflictError(message, details)

        assert error.message == message
        assert error.error_code == "SERVICE_CONFLICT"
        assert error.status_code == status.HTTP_409_CONFLICT
        assert error.details == expected_details
        assert str(error) == message


class TestScheduleCannotBeDeletedError:
    """ScheduleCannotBeDeletedError 測試。"""

    def test_schedule_cannot_be_deleted_error_inheritance(self) -> None:
        """測試 ScheduleCannotBeDeletedError 繼承關係。"""
        error = ScheduleCannotBeDeletedError(123)

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "SERVICE_SCHEDULE_CANNOT_BE_DELETED"
        assert error.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.parametrize(
        "schedule_id,details,expected_details",
        [
            # 基本測試
            (123, None, {}),
            ("abc123", None, {}),
            # 邊界測試：空詳細資訊
            (123, {}, {}),
            # 帶詳細資訊測試
            (
                123,
                {"reason": "schedule_already_accepted"},
                {"reason": "schedule_already_accepted"},
            ),
        ],
    )
    def test_schedule_cannot_be_deleted_error_creation(
        self,
        schedule_id: int | str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 ScheduleCannotBeDeletedError 建立功能。"""
        error = ScheduleCannotBeDeletedError(schedule_id, details)

        assert error.message == f"時段無法刪除: ID={schedule_id}"
        assert error.error_code == "SERVICE_SCHEDULE_CANNOT_BE_DELETED"
        assert error.status_code == status.HTTP_409_CONFLICT
        assert error.details == expected_details
        assert str(error) == f"時段無法刪除: ID={schedule_id}"


class TestScheduleOverlapError:
    """ScheduleOverlapError 測試。"""

    def test_schedule_overlap_error_inheritance(self) -> None:
        """測試 ScheduleOverlapError 繼承關係。"""
        error = ScheduleOverlapError("測試錯誤")

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "SERVICE_SCHEDULE_OVERLAP"
        assert error.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.parametrize(
        "message,details,expected_details",
        [
            # 基本測試
            ("時段時間重疊", None, {}),
            # 邊界測試：空詳細資訊
            ("時段時間重疊", {}, {}),
            # 帶詳細資訊測試
            (
                "時段時間重疊",
                {
                    "existing_schedule_id": 123,
                    "overlap_start": "09:00",
                    "overlap_end": "10:00",
                },
                {
                    "existing_schedule_id": 123,
                    "overlap_start": "09:00",
                    "overlap_end": "10:00",
                },
            ),
        ],
    )
    def test_schedule_overlap_error_creation(
        self,
        message: str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 ScheduleOverlapError 建立功能。"""
        error = ScheduleOverlapError(message, details)

        assert error.message == message
        assert error.error_code == "SERVICE_SCHEDULE_OVERLAP"
        assert error.status_code == status.HTTP_409_CONFLICT
        assert error.details == expected_details
        assert str(error) == message


# ===== System 層級錯誤 =====
class TestServiceUnavailableError:
    """ServiceUnavailableError 測試。"""

    def test_service_unavailable_error_inheritance(self) -> None:
        """測試 ServiceUnavailableError 繼承關係。"""
        error = ServiceUnavailableError("測試錯誤")

        # 測試繼承關係
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)

        # 測試固定屬性
        assert error.error_code == "SERVICE_UNAVAILABLE"
        assert error.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    @pytest.mark.parametrize(
        "message,details,expected_details",
        [
            # 基本測試
            ("服務暫時不可用", None, {}),
            # 邊界測試：空詳細資訊
            ("服務暫時不可用", {}, {}),
            # 帶詳細資訊測試
            ("維護中", {"duration": "2小時"}, {"duration": "2小時"}),
        ],
    )
    def test_service_unavailable_error_creation(
        self,
        message: str,
        details: dict | None,
        expected_details: dict,
    ) -> None:
        """測試 ServiceUnavailableError 建立功能。"""
        error = ServiceUnavailableError(message, details)

        assert error.message == message
        assert error.error_code == "SERVICE_UNAVAILABLE"
        assert error.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert error.details == expected_details
        assert str(error) == message
