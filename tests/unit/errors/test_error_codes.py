"""
錯誤代碼測試模組。

測試各種錯誤代碼常數。
"""

# ===== 本地模組 =====
from app.errors.error_codes.cors import CORSErrorCode
from app.errors.error_codes.crud import CRUDErrorCode
from app.errors.error_codes.router import RouterErrorCode
from app.errors.error_codes.service import ServiceErrorCode
from app.errors.error_codes.system import SystemErrorCode


class TestCORSErrorCode:
    """CORSErrorCode 測試。"""

    def test_cors_error_code_values(self):
        """測試 CORS 錯誤代碼值。"""
        # Given: 準備預期的錯誤代碼值
        expected_values = {
            "ORIGIN_NOT_ALLOWED": "CORS_ORIGIN_NOT_ALLOWED",
            "METHOD_NOT_ALLOWED": "CORS_METHOD_NOT_ALLOWED",
            "HEADER_NOT_ALLOWED": "CORS_HEADER_NOT_ALLOWED",
        }

        # When: 檢查錯誤代碼值

        # Then: 驗證所有錯誤代碼都有正確的值
        assert CORSErrorCode.ORIGIN_NOT_ALLOWED == expected_values["ORIGIN_NOT_ALLOWED"]
        assert CORSErrorCode.METHOD_NOT_ALLOWED == expected_values["METHOD_NOT_ALLOWED"]
        assert CORSErrorCode.HEADER_NOT_ALLOWED == expected_values["HEADER_NOT_ALLOWED"]

    def test_cors_error_code_format(self):
        """測試 CORS 錯誤代碼格式。"""
        # Given: 準備所有 CORS 錯誤代碼
        error_codes = [
            CORSErrorCode.ORIGIN_NOT_ALLOWED,
            CORSErrorCode.METHOD_NOT_ALLOWED,
            CORSErrorCode.HEADER_NOT_ALLOWED,
        ]

        # When: 檢查每個錯誤代碼的格式
        for code in error_codes:
            # Then: 驗證錯誤代碼以 CORS_ 開頭，且大寫
            assert code.startswith("CORS_")
            assert code.isupper()

    def test_cors_error_code_uniqueness(self):
        """測試 CORS 錯誤代碼唯一性。"""
        # Given: 準備所有 CORS 錯誤代碼
        error_codes = [
            CORSErrorCode.ORIGIN_NOT_ALLOWED,
            CORSErrorCode.METHOD_NOT_ALLOWED,
            CORSErrorCode.HEADER_NOT_ALLOWED,
        ]

        # When: 檢查錯誤代碼唯一性

        # Then: 確保所有錯誤代碼都是唯一的
        assert len(error_codes) == len(set(error_codes))


class TestCRUDErrorCode:
    """CRUDErrorCode 測試。"""

    def test_crud_error_code_values(self):
        """測試 CRUD 錯誤代碼值。"""
        # Given: 準備預期的錯誤代碼值
        expected_values = {
            "BAD_REQUEST": "CRUD_BAD_REQUEST",
            "RECORD_NOT_FOUND": "CRUD_RECORD_NOT_FOUND",
            "CONSTRAINT_VIOLATION": "CRUD_CONSTRAINT_VIOLATION",
            "DATABASE_ERROR": "CRUD_DATABASE_ERROR",
            "CONNECTION_ERROR": "CRUD_CONNECTION_ERROR",
        }

        # When: 檢查錯誤代碼值

        # Then: 驗證所有錯誤代碼都有正確的值
        assert CRUDErrorCode.BAD_REQUEST == expected_values["BAD_REQUEST"]
        assert CRUDErrorCode.RECORD_NOT_FOUND == expected_values["RECORD_NOT_FOUND"]
        assert (
            CRUDErrorCode.CONSTRAINT_VIOLATION
            == expected_values["CONSTRAINT_VIOLATION"]
        )
        assert CRUDErrorCode.DATABASE_ERROR == expected_values["DATABASE_ERROR"]
        assert CRUDErrorCode.CONNECTION_ERROR == expected_values["CONNECTION_ERROR"]

    def test_crud_error_code_format(self):
        """測試 CRUD 錯誤代碼格式。"""
        # Given: 準備所有 CRUD 錯誤代碼
        error_codes = [
            CRUDErrorCode.BAD_REQUEST,
            CRUDErrorCode.RECORD_NOT_FOUND,
            CRUDErrorCode.CONSTRAINT_VIOLATION,
            CRUDErrorCode.DATABASE_ERROR,
            CRUDErrorCode.CONNECTION_ERROR,
        ]

        # When: 檢查每個錯誤代碼的格式
        for code in error_codes:
            # Then: 驗證錯誤代碼以 CRUD_ 開頭，且大寫
            assert code.startswith("CRUD_")
            assert code.isupper()

    def test_crud_error_code_uniqueness(self):
        """測試 CRUD 錯誤代碼唯一性。"""
        # Given: 準備所有 CRUD 錯誤代碼
        error_codes = [
            CRUDErrorCode.BAD_REQUEST,
            CRUDErrorCode.RECORD_NOT_FOUND,
            CRUDErrorCode.CONSTRAINT_VIOLATION,
            CRUDErrorCode.DATABASE_ERROR,
            CRUDErrorCode.CONNECTION_ERROR,
        ]

        # When: 檢查錯誤代碼唯一性

        # Then: 確保所有錯誤代碼都是唯一的
        assert len(error_codes) == len(set(error_codes))


class TestRouterErrorCode:
    """RouterErrorCode 測試。"""

    def test_router_error_code_values(self):
        """測試路由錯誤代碼值。"""
        # Given: 準備預期的錯誤代碼值
        expected_values = {
            "BAD_REQUEST": "ROUTER_BAD_REQUEST",
            "INVALID_METHOD": "ROUTER_INVALID_METHOD",
            "INVALID_SCHEDULE_TIME": "ROUTER_INVALID_SCHEDULE_TIME",
            "AUTHENTICATION_ERROR": "ROUTER_AUTHENTICATION_ERROR",
            "AUTHORIZATION_ERROR": "ROUTER_AUTHORIZATION_ERROR",
            "ENDPOINT_NOT_FOUND": "ROUTER_ENDPOINT_NOT_FOUND",
            "SCHEDULE_NOT_FOUND": "ROUTER_SCHEDULE_NOT_FOUND",
            "VALIDATION_ERROR": "ROUTER_VALIDATION_ERROR",
        }

        # When: 檢查錯誤代碼值

        # Then: 驗證所有錯誤代碼都有正確的值
        assert RouterErrorCode.BAD_REQUEST == expected_values["BAD_REQUEST"]
        assert RouterErrorCode.INVALID_METHOD == expected_values["INVALID_METHOD"]
        assert (
            RouterErrorCode.INVALID_SCHEDULE_TIME
            == expected_values["INVALID_SCHEDULE_TIME"]
        )
        assert (
            RouterErrorCode.AUTHENTICATION_ERROR
            == expected_values["AUTHENTICATION_ERROR"]
        )
        assert (
            RouterErrorCode.AUTHORIZATION_ERROR
            == expected_values["AUTHORIZATION_ERROR"]
        )
        assert (
            RouterErrorCode.ENDPOINT_NOT_FOUND == expected_values["ENDPOINT_NOT_FOUND"]
        )
        assert (
            RouterErrorCode.SCHEDULE_NOT_FOUND == expected_values["SCHEDULE_NOT_FOUND"]
        )
        assert RouterErrorCode.VALIDATION_ERROR == expected_values["VALIDATION_ERROR"]

    def test_router_error_code_format(self):
        """測試路由錯誤代碼格式。"""
        # Given: 準備所有 Router 錯誤代碼
        error_codes = [
            RouterErrorCode.BAD_REQUEST,
            RouterErrorCode.INVALID_METHOD,
            RouterErrorCode.INVALID_SCHEDULE_TIME,
            RouterErrorCode.AUTHENTICATION_ERROR,
            RouterErrorCode.AUTHORIZATION_ERROR,
            RouterErrorCode.ENDPOINT_NOT_FOUND,
            RouterErrorCode.SCHEDULE_NOT_FOUND,
            RouterErrorCode.VALIDATION_ERROR,
        ]

        # When: 檢查每個錯誤代碼的格式
        for code in error_codes:
            # Then: 驗證錯誤代碼以 ROUTER_ 開頭，且大寫
            assert code.startswith("ROUTER_")
            assert code.isupper()

    def test_router_error_code_uniqueness(self):
        """測試路由錯誤代碼唯一性。"""
        # Given: 準備所有 Router 錯誤代碼
        error_codes = [
            RouterErrorCode.BAD_REQUEST,
            RouterErrorCode.INVALID_METHOD,
            RouterErrorCode.INVALID_SCHEDULE_TIME,
            RouterErrorCode.AUTHENTICATION_ERROR,
            RouterErrorCode.AUTHORIZATION_ERROR,
            RouterErrorCode.ENDPOINT_NOT_FOUND,
            RouterErrorCode.SCHEDULE_NOT_FOUND,
            RouterErrorCode.VALIDATION_ERROR,
        ]

        # When: 檢查錯誤代碼唯一性

        # Then: 確保所有錯誤代碼都是唯一的
        assert len(error_codes) == len(set(error_codes))


class TestServiceErrorCode:
    """ServiceErrorCode 測試。"""

    def test_service_error_code_values(self):
        """測試服務錯誤代碼值。"""
        # Given: 準備預期的錯誤代碼值
        expected_values = {
            "BUSINESS_LOGIC_ERROR": "SERVICE_BUSINESS_LOGIC_ERROR",
            "SCHEDULE_OVERLAP": "SERVICE_SCHEDULE_OVERLAP",
            "INVALID_OPERATION": "SERVICE_INVALID_OPERATION",
            "USER_NOT_FOUND": "SERVICE_USER_NOT_FOUND",
            "SCHEDULE_NOT_FOUND": "SERVICE_SCHEDULE_NOT_FOUND",
            "CONFLICT": "SERVICE_CONFLICT",
            "SCHEDULE_CANNOT_BE_DELETED": "SERVICE_SCHEDULE_CANNOT_BE_DELETED",
        }

        # When: 檢查錯誤代碼值

        # Then: 驗證所有錯誤代碼都有正確的值
        assert (
            ServiceErrorCode.BUSINESS_LOGIC_ERROR
            == expected_values["BUSINESS_LOGIC_ERROR"]
        )
        assert ServiceErrorCode.SCHEDULE_OVERLAP == expected_values["SCHEDULE_OVERLAP"]
        assert (
            ServiceErrorCode.INVALID_OPERATION == expected_values["INVALID_OPERATION"]
        )
        assert ServiceErrorCode.USER_NOT_FOUND == expected_values["USER_NOT_FOUND"]
        assert (
            ServiceErrorCode.SCHEDULE_NOT_FOUND == expected_values["SCHEDULE_NOT_FOUND"]
        )
        assert ServiceErrorCode.CONFLICT == expected_values["CONFLICT"]
        assert (
            ServiceErrorCode.SCHEDULE_CANNOT_BE_DELETED
            == expected_values["SCHEDULE_CANNOT_BE_DELETED"]
        )

    def test_service_error_code_format(self):
        """測試服務錯誤代碼格式。"""
        # Given: 準備所有 Service 錯誤代碼
        error_codes = [
            ServiceErrorCode.BUSINESS_LOGIC_ERROR,
            ServiceErrorCode.SCHEDULE_OVERLAP,
            ServiceErrorCode.INVALID_OPERATION,
            ServiceErrorCode.USER_NOT_FOUND,
            ServiceErrorCode.SCHEDULE_NOT_FOUND,
            ServiceErrorCode.CONFLICT,
            ServiceErrorCode.SCHEDULE_CANNOT_BE_DELETED,
        ]

        # When: 檢查每個錯誤代碼的格式
        for code in error_codes:
            # Then: 驗證錯誤代碼以 SERVICE_ 開頭，且大寫
            assert code.startswith("SERVICE_")
            assert code.isupper()

    def test_service_error_code_uniqueness(self):
        """測試服務錯誤代碼唯一性。"""
        # Given: 準備所有 Service 錯誤代碼
        error_codes = [
            ServiceErrorCode.BUSINESS_LOGIC_ERROR,
            ServiceErrorCode.SCHEDULE_OVERLAP,
            ServiceErrorCode.INVALID_OPERATION,
            ServiceErrorCode.USER_NOT_FOUND,
            ServiceErrorCode.SCHEDULE_NOT_FOUND,
            ServiceErrorCode.CONFLICT,
            ServiceErrorCode.SCHEDULE_CANNOT_BE_DELETED,
        ]

        # When: 檢查錯誤代碼唯一性

        # Then: 確保所有錯誤代碼都是唯一的
        assert len(error_codes) == len(set(error_codes))


class TestSystemErrorCode:
    """SystemErrorCode 測試。"""

    def test_system_error_code_values(self):
        """測試系統錯誤代碼值。"""
        # Given: 準備預期的錯誤代碼值
        expected_values = {
            "INTERNAL_ERROR": "INTERNAL_ERROR",
            "SERVICE_UNAVAILABLE": "SERVICE_UNAVAILABLE",
            "LIVENESS_CHECK_ERROR": "LIVENESS_CHECK_ERROR",
            "READINESS_CHECK_ERROR": "READINESS_CHECK_ERROR",
        }

        # When: 檢查錯誤代碼值

        # Then: 驗證所有錯誤代碼都有正確的值
        assert SystemErrorCode.INTERNAL_ERROR == expected_values["INTERNAL_ERROR"]
        assert (
            SystemErrorCode.SERVICE_UNAVAILABLE
            == expected_values["SERVICE_UNAVAILABLE"]
        )
        assert (
            SystemErrorCode.LIVENESS_CHECK_ERROR
            == expected_values["LIVENESS_CHECK_ERROR"]
        )
        assert (
            SystemErrorCode.READINESS_CHECK_ERROR
            == expected_values["READINESS_CHECK_ERROR"]
        )

    def test_system_error_code_format(self):
        """測試系統錯誤代碼格式。"""
        # Given: 準備所有 System 錯誤代碼
        error_codes = [
            SystemErrorCode.INTERNAL_ERROR,
            SystemErrorCode.SERVICE_UNAVAILABLE,
            SystemErrorCode.LIVENESS_CHECK_ERROR,
            SystemErrorCode.READINESS_CHECK_ERROR,
        ]

        # When: 檢查每個錯誤代碼的格式
        for code in error_codes:
            # Then: 驗證格式要求，系統錯誤代碼沒有統一前綴，但必須是大寫
            assert code.isupper()

    def test_system_error_code_uniqueness(self):
        """測試系統錯誤代碼唯一性。"""
        # Given: 準備所有 System 錯誤代碼
        error_codes = [
            SystemErrorCode.INTERNAL_ERROR,
            SystemErrorCode.SERVICE_UNAVAILABLE,
            SystemErrorCode.LIVENESS_CHECK_ERROR,
            SystemErrorCode.READINESS_CHECK_ERROR,
        ]

        # When: 檢查錯誤代碼唯一性

        # Then: 確保所有錯誤代碼都是唯一的
        assert len(error_codes) == len(set(error_codes))


class TestErrorCodeConsistency:
    """錯誤代碼一致性測試。"""

    def test_all_error_codes_are_strings(self):
        """測試所有錯誤代碼都是字串。"""
        # Given: 收集所有錯誤代碼
        all_codes = []

        # Given: CORS 錯誤代碼
        all_codes.extend(
            [
                CORSErrorCode.ORIGIN_NOT_ALLOWED,
                CORSErrorCode.METHOD_NOT_ALLOWED,
                CORSErrorCode.HEADER_NOT_ALLOWED,
            ]
        )

        # Given: CRUD 錯誤代碼
        all_codes.extend(
            [
                CRUDErrorCode.BAD_REQUEST,
                CRUDErrorCode.RECORD_NOT_FOUND,
                CRUDErrorCode.CONSTRAINT_VIOLATION,
                CRUDErrorCode.DATABASE_ERROR,
                CRUDErrorCode.CONNECTION_ERROR,
            ]
        )

        # Given: Router 錯誤代碼
        all_codes.extend(
            [
                RouterErrorCode.BAD_REQUEST,
                RouterErrorCode.INVALID_METHOD,
                RouterErrorCode.INVALID_SCHEDULE_TIME,
                RouterErrorCode.AUTHENTICATION_ERROR,
                RouterErrorCode.AUTHORIZATION_ERROR,
                RouterErrorCode.ENDPOINT_NOT_FOUND,
                RouterErrorCode.SCHEDULE_NOT_FOUND,
                RouterErrorCode.VALIDATION_ERROR,
            ]
        )

        # Given: Service 錯誤代碼
        all_codes.extend(
            [
                ServiceErrorCode.BUSINESS_LOGIC_ERROR,
                ServiceErrorCode.SCHEDULE_OVERLAP,
                ServiceErrorCode.INVALID_OPERATION,
                ServiceErrorCode.USER_NOT_FOUND,
                ServiceErrorCode.SCHEDULE_NOT_FOUND,
                ServiceErrorCode.CONFLICT,
                ServiceErrorCode.SCHEDULE_CANNOT_BE_DELETED,
            ]
        )

        # Given: System 錯誤代碼
        all_codes.extend(
            [
                SystemErrorCode.INTERNAL_ERROR,
                SystemErrorCode.SERVICE_UNAVAILABLE,
                SystemErrorCode.LIVENESS_CHECK_ERROR,
                SystemErrorCode.READINESS_CHECK_ERROR,
            ]
        )

        # When: 檢查每個錯誤代碼的類型
        for code in all_codes:
            # Then: 驗證所有錯誤代碼都是字串，且不為空
            assert isinstance(code, str)
            assert len(code) > 0

    def test_error_code_prefixes(self):
        """測試錯誤代碼前綴。"""
        # Given: 準備各層級的錯誤代碼
        cors_codes = [
            CORSErrorCode.ORIGIN_NOT_ALLOWED,
            CORSErrorCode.METHOD_NOT_ALLOWED,
            CORSErrorCode.HEADER_NOT_ALLOWED,
        ]

        crud_codes = [
            CRUDErrorCode.BAD_REQUEST,
            CRUDErrorCode.RECORD_NOT_FOUND,
            CRUDErrorCode.CONSTRAINT_VIOLATION,
            CRUDErrorCode.DATABASE_ERROR,
            CRUDErrorCode.CONNECTION_ERROR,
        ]

        router_codes = [
            RouterErrorCode.BAD_REQUEST,
            RouterErrorCode.INVALID_METHOD,
            RouterErrorCode.INVALID_SCHEDULE_TIME,
            RouterErrorCode.AUTHENTICATION_ERROR,
            RouterErrorCode.AUTHORIZATION_ERROR,
            RouterErrorCode.ENDPOINT_NOT_FOUND,
            RouterErrorCode.SCHEDULE_NOT_FOUND,
            RouterErrorCode.VALIDATION_ERROR,
        ]

        service_codes = [
            ServiceErrorCode.BUSINESS_LOGIC_ERROR,
            ServiceErrorCode.SCHEDULE_OVERLAP,
            ServiceErrorCode.INVALID_OPERATION,
            ServiceErrorCode.USER_NOT_FOUND,
            ServiceErrorCode.SCHEDULE_NOT_FOUND,
            ServiceErrorCode.CONFLICT,
            ServiceErrorCode.SCHEDULE_CANNOT_BE_DELETED,
        ]

        system_codes = [
            SystemErrorCode.INTERNAL_ERROR,
            SystemErrorCode.SERVICE_UNAVAILABLE,
            SystemErrorCode.LIVENESS_CHECK_ERROR,
            SystemErrorCode.READINESS_CHECK_ERROR,
        ]

        # When: 檢查每個層級的錯誤代碼前綴
        for code in cors_codes:
            # Then: 驗證錯誤代碼以 CORS_ 開頭，且大寫
            assert code.startswith("CORS_")
            assert code.isupper()

        for code in crud_codes:
            # Then: 驗證錯誤代碼以 CRUD_ 開頭，且大寫
            assert code.startswith("CRUD_")
            assert code.isupper()

        for code in router_codes:
            # Then: 驗證錯誤代碼以 ROUTER_ 開頭，且大寫
            assert code.startswith("ROUTER_")
            assert code.isupper()

        for code in service_codes:
            # Then: 驗證錯誤代碼以 SERVICE_ 開頭，且大寫
            assert code.startswith("SERVICE_")
            assert code.isupper()

        for code in system_codes:
            # Then: 驗證錯誤代碼沒有統一前綴，但都必須是大寫
            assert code.isupper()

    def test_error_code_naming_convention(self):
        """測試錯誤代碼命名慣例。"""
        # Given: 收集所有錯誤代碼
        all_codes = []

        # Given: 使用反射獲取所有錯誤代碼
        for error_code_class in [
            CORSErrorCode,
            CRUDErrorCode,
            RouterErrorCode,
            ServiceErrorCode,
            SystemErrorCode,
        ]:
            # 使用 dir() 函數遍歷錯誤代碼類別中的所有屬性名稱
            for attr_name in dir(error_code_class):
                # 過濾掉私有屬性（以底線開頭的屬性，如 __init__, __doc__ 等）
                if not attr_name.startswith("_"):
                    # 使用 getattr() 動態取得該屬性的值
                    attr_value = getattr(error_code_class, attr_name)
                    # 確保屬性值是字串類型（錯誤代碼應該是字串）
                    if isinstance(attr_value, str):
                        # 將符合條件的錯誤代碼字串加入到收集列表中
                        all_codes.append(attr_value)

        # When: 檢查每個錯誤代碼的命名慣例
        for code in all_codes:
            # Then: 驗證錯誤代碼應該是大寫字母和底線
            assert code.isupper() or "_" in code
            # Then: 驗證錯誤代碼不應該包含空格
            assert " " not in code
            # Then: 驗證錯誤代碼不應該包含特殊字符（除了底線）
            assert code.replace("_", "").isalnum()
