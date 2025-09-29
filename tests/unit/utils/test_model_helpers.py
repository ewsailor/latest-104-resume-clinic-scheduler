"""模型輔助工具測試。"""

# ===== 標準函式庫 =====
from datetime import datetime

# ===== 本地模組 =====
from app.utils.model_helpers import (
    format_datetime,
    safe_getattr,
)

# ===== 第三方套件 =====


class TestModelHelper:
    """model_helpers 工具函式測試。"""

    # ===== format_datetime =====
    def test_format_datetime_with_valid_datetime(self):
        """測試格式化日期時間 - 有效日期時間。"""
        # GIVEN：建立一個有效的日期時間物件
        dt = datetime(2024, 1, 15, 12, 30, 45)

        # WHEN：呼叫格式化函數
        result = format_datetime(dt)

        # THEN：確認返回正確的 ISO 格式字串
        assert result == "2024-01-15T12:30:45"

    def test_format_datetime_with_none(self):
        """測試格式化日期時間 - None 值。"""
        # GIVEN：提供 None 值作為輸入
        dt = None

        # WHEN：呼叫格式化函數
        result = format_datetime(dt)

        # THEN：確認返回 None
        assert result is None

    # ===== safe_getattr =====
    def setup_method(self):
        """每個測試前的初始化，建立測試用的物件實例。"""

        class SampleObject:
            def __init__(self):
                self.name = "test"

        self.sample_object = SampleObject()

    def _create_bad_object(self):
        """建立會拋出例外的測試物件。"""

        class BadObj:
            def __getattribute__(self, name):
                raise Exception("error")

        return BadObj()

    def test_safe_getattr_existing_attribute(self):
        """測試安全取得屬性 - 存在的屬性。"""
        # GIVEN：使用已設定的測試物件

        # WHEN：嘗試取得存在的屬性
        result = safe_getattr(self.sample_object, "name")

        # THEN：確認返回正確的屬性值
        assert result == "test"

    def test_safe_getattr_missing_attribute(self):
        """測試安全取得屬性 - 不存在的屬性（無預設值）。"""
        # GIVEN：建立一個沒有該屬性的物件
        obj = object()

        # WHEN：嘗試取得不存在的屬性
        result = safe_getattr(obj, "missing")

        # THEN：確認返回 None（預設值）
        assert result is None

    def test_safe_getattr_missing_attribute_with_default(self):
        """測試安全取得屬性 - 不存在的屬性（有預設值）。"""
        # GIVEN：建立一個沒有該屬性的物件
        obj = object()

        # WHEN：嘗試取得不存在的屬性並提供預設值
        result = safe_getattr(obj, "missing", "default")

        # THEN：確認返回提供的預設值
        assert result == "default"

    def test_safe_getattr_exception_handling_without_default(self):
        """測試安全取得屬性 - 例外處理（無預設值）。"""
        # GIVEN：建立一個會拋出例外的物件
        bad_obj = self._create_bad_object()

        # WHEN：嘗試取得屬性（會觸發例外）
        result = safe_getattr(bad_obj, "any")

        # THEN：確認例外被捕捉並返回 None
        assert result is None

    def test_safe_getattr_exception_handling_with_default(self):
        """測試安全取得屬性 - 例外處理（有預設值）。"""
        # GIVEN：建立一個會拋出例外的物件
        bad_obj = self._create_bad_object()

        # WHEN：嘗試取得屬性（會觸發例外）
        result = safe_getattr(bad_obj, "any", "fallback")

        # THEN：確認例外被捕捉並返回預設值
        assert result == "fallback"
