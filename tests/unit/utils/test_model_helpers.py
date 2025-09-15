"""
模型輔助工具測試。

測試模型輔助工具模組的功能。
"""

# ===== 標準函式庫 =====
from datetime import datetime
from unittest.mock import Mock

# ===== 本地模組 =====
from app.utils.model_helpers import format_datetime, safe_getattr


# ===== 測試設定 =====
class TestModelHelpers:
    """模型輔助工具測試類別。"""

    def test_format_datetime_with_datetime(self):
        """測試格式化日期時間 - 有日期時間物件。"""
        dt = datetime(2024, 1, 15, 12, 30, 45)
        result = format_datetime(dt)
        assert result == "2024-01-15T12:30:45"

    def test_format_datetime_with_none(self):
        """測試格式化日期時間 - None 值。"""
        result = format_datetime(None)
        assert result is None

    def test_format_datetime_with_false(self):
        """測試格式化日期時間 - False 值。"""
        result = format_datetime(False)
        assert result is None

    def test_format_datetime_with_empty_string(self):
        """測試格式化日期時間 - 空字串。"""
        result = format_datetime("")
        assert result is None

    def test_format_datetime_with_zero(self):
        """測試格式化日期時間 - 0 值。"""
        result = format_datetime(0)
        assert result is None

    def test_format_datetime_with_datetime_with_microseconds(self):
        """測試格式化日期時間 - 包含微秒。"""
        dt = datetime(2024, 1, 15, 12, 30, 45, 123456)
        result = format_datetime(dt)
        assert result == "2024-01-15T12:30:45.123456"

    def test_safe_getattr_existing_attribute(self):
        """測試安全取得屬性 - 屬性存在。"""
        obj = Mock()
        obj.test_attr = "test_value"

        result = safe_getattr(obj, "test_attr")
        assert result == "test_value"

    def test_safe_getattr_missing_attribute_with_default(self):
        """測試安全取得屬性 - 屬性不存在，有預設值。"""
        obj = object()  # 使用普通物件而不是 Mock

        result = safe_getattr(obj, "missing_attr", "default_value")
        assert result == "default_value"

    def test_safe_getattr_missing_attribute_no_default(self):
        """測試安全取得屬性 - 屬性不存在，無預設值。"""
        obj = object()  # 使用普通物件而不是 Mock

        result = safe_getattr(obj, "missing_attr")
        assert result is None

    def test_safe_getattr_exception_handling(self):
        """測試安全取得屬性 - 例外處理。"""

        class ProblematicObject:
            def __getattribute__(self, name):
                if name == "any_attr":
                    raise Exception("模擬錯誤")
                return super().__getattribute__(name)

        obj = ProblematicObject()

        result = safe_getattr(obj, "any_attr", "fallback_value")
        assert result == "fallback_value"

    def test_safe_getattr_with_complex_object(self):
        """測試安全取得屬性 - 複雜物件。"""

        class TestClass:
            def __init__(self):
                self.public_attr = "public"
                self._private_attr = "private"

        obj = TestClass()

        # 測試存在的屬性
        assert safe_getattr(obj, "public_attr") == "public"
        assert safe_getattr(obj, "_private_attr") == "private"

        # 測試不存在的屬性
        assert safe_getattr(obj, "non_existent") is None
        assert safe_getattr(obj, "non_existent", "default") == "default"

    def test_safe_getattr_with_none_object(self):
        """測試安全取得屬性 - None 物件。"""
        result = safe_getattr(None, "any_attr", "default")
        assert result == "default"

    def test_safe_getattr_with_string_object(self):
        """測試安全取得屬性 - 字串物件。"""
        result = safe_getattr("hello", "upper", "default")
        assert result != "default"  # upper 方法存在，所以不會返回預設值
        assert callable(result)  # upper 是一個方法

    def test_safe_getattr_with_list_object(self):
        """測試安全取得屬性 - 列表物件。"""
        obj = [1, 2, 3]

        # 測試存在的方法
        result = safe_getattr(obj, "append", "default")
        assert result != "default"  # append 方法存在，所以不會返回預設值
        assert callable(result)  # append 是一個方法

        # 測試不存在的屬性
        result = safe_getattr(obj, "non_existent", "default")
        assert result == "default"

    def test_safe_getattr_with_dict_object(self):
        """測試安全取得屬性 - 字典物件。"""
        obj = {"key": "value"}

        # 測試存在的方法
        result = safe_getattr(obj, "keys", "default")
        assert result != "default"  # keys 方法存在，所以不會返回預設值
        assert callable(result)  # keys 是一個方法

        # 測試不存在的屬性
        result = safe_getattr(obj, "non_existent", "default")
        assert result == "default"

    def test_safe_getattr_with_custom_exception(self):
        """測試安全取得屬性 - 自定義例外。"""

        class CustomException(Exception):
            pass

        class ProblematicObject:
            def __getattribute__(self, name):
                if name == "any_attr":
                    raise CustomException("自定義錯誤")
                return super().__getattribute__(name)

        obj = ProblematicObject()

        result = safe_getattr(obj, "any_attr", "fallback")
        assert result == "fallback"

    def test_safe_getattr_with_attribute_error(self):
        """測試安全取得屬性 - AttributeError。"""

        class ProblematicObject:
            def __getattribute__(self, name):
                if name == "any_attr":
                    raise AttributeError("屬性不存在")
                return super().__getattribute__(name)

        obj = ProblematicObject()

        result = safe_getattr(obj, "any_attr", "fallback")
        assert result == "fallback"

    def test_safe_getattr_with_type_error(self):
        """測試安全取得屬性 - TypeError。"""

        class ProblematicObject:
            def __getattribute__(self, name):
                if name == "any_attr":
                    raise TypeError("類型錯誤")
                return super().__getattribute__(name)

        obj = ProblematicObject()

        result = safe_getattr(obj, "any_attr", "fallback")
        assert result == "fallback"
