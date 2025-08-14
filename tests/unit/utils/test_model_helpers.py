"""
模型輔助工具測試模組。

測試共用的模型相關工具函式。
"""

from datetime import date, datetime, time

import pytest

from app.utils.model_helpers import format_datetime, safe_getattr
from tests.logger import log_test_info


class TestModelHelpers:
    """模型輔助工具測試類別。"""

    def test_format_datetime_with_datetime(self):
        """測試格式化 datetime 物件。"""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = format_datetime(dt)
        assert result == "2024-01-15T10:30:00"

    def test_format_datetime_with_date(self):
        """測試格式化 date 物件。"""
        d = date(2024, 1, 15)
        result = format_datetime(d)
        assert result == "2024-01-15"

    def test_format_datetime_with_time(self):
        """測試格式化 time 物件。"""
        t = time(10, 30, 0)
        result = format_datetime(t)
        assert result == "10:30:00"

    def test_format_datetime_with_none(self):
        """測試格式化 None 值。"""
        result = format_datetime(None)
        assert result is None

    def test_safe_getattr_existing_attr(self):
        """測試安全取得存在的屬性。"""

        class TestObj:
            def __init__(self):
                self.test_attr = "test_value"

        obj = TestObj()
        result = safe_getattr(obj, 'test_attr')
        assert result == "test_value"

    def test_safe_getattr_missing_attr_with_default(self):
        """測試安全取得不存在的屬性（有預設值）。"""

        class TestObj:
            pass

        obj = TestObj()
        result = safe_getattr(obj, 'missing_attr', 'default_value')
        assert result == "default_value"

    def test_safe_getattr_missing_attr_no_default(self):
        """測試安全取得不存在的屬性（無預設值）。"""

        class TestObj:
            pass

        obj = TestObj()
        result = safe_getattr(obj, 'missing_attr')
        assert result is None

    def test_safe_getattr_with_exception(self):
        """測試安全取得屬性時發生異常。"""

        class TestObj:
            @property
            def problematic_attr(self):
                raise Exception("測試異常")

        obj = TestObj()
        result = safe_getattr(obj, 'problematic_attr', 'fallback_value')
        assert result == "fallback_value"
