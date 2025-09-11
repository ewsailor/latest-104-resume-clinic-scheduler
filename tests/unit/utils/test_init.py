"""
工具模組初始化測試。

測試工具模組的導入和配置。
"""

from datetime import datetime, timedelta, timezone
import inspect

# ===== 標準函式庫 =====
import pytest

# ===== 本地模組 =====
from app.utils import TAIWAN_TIMEZONE
from app.utils import TAIWAN_TIMEZONE as tz
from app.utils import TAIWAN_TIMEZONE as tz1
from app.utils import get_local_now_naive
from app.utils import get_local_now_naive as get_local
from app.utils import get_utc_timestamp
from app.utils import get_utc_timestamp as get_utc
from app.utils.timezone import TAIWAN_TIMEZONE as tz2

# ===== 測試設定 =====


class TestUtilsInit:
    """工具模組初始化測試類別。"""

    def test_taiwan_timezone_import(self):
        """測試台灣時區常數導入。"""
        assert TAIWAN_TIMEZONE is not None
        assert hasattr(TAIWAN_TIMEZONE, 'utcoffset')

    def test_get_local_now_naive_import(self):
        """測試取得本地時間函數導入。"""
        assert get_local_now_naive is not None
        assert callable(get_local_now_naive)

    def test_get_utc_timestamp_import(self):
        """測試取得 UTC 時間戳記函數導入。"""
        assert get_utc_timestamp is not None
        assert callable(get_utc_timestamp)

    def test_taiwan_timezone_type(self):
        """測試台灣時區類型。"""
        assert isinstance(TAIWAN_TIMEZONE, timezone)

    def test_get_local_now_naive_return_type(self):
        """測試取得本地時間返回類型。"""
        result = get_local_now_naive()
        assert isinstance(result, datetime)
        assert result.tzinfo is None  # 應該是 naive datetime

    def test_get_utc_timestamp_return_type(self):
        """測試取得 UTC 時間戳記返回類型。"""
        result = get_utc_timestamp()
        assert isinstance(result, str)
        assert result.endswith('Z')
        assert 'T' in result

    def test_taiwan_timezone_offset(self):
        """測試台灣時區偏移量。"""
        expected_offset = timedelta(hours=8)
        assert TAIWAN_TIMEZONE.utcoffset(None) == expected_offset

    def test_imported_functions_are_callable(self):
        """測試導入的函數都是可調用的。"""
        functions = [get_local_now_naive, get_utc_timestamp]

        for func in functions:
            assert callable(func), f"{func.__name__} should be callable"

    def test_imported_constants_are_accessible(self):
        """測試導入的常數都是可訪問的。"""
        constants = [TAIWAN_TIMEZONE]

        for const in constants:
            assert const is not None, f"{const} should not be None"

    def test_module_level_imports(self):
        """測試模組級別導入。"""
        # 測試可以從模組直接導入
        assert tz is TAIWAN_TIMEZONE
        assert get_local is get_local_now_naive
        assert get_utc is get_utc_timestamp

    def test_imported_functions_have_correct_signatures(self):
        """測試導入的函數有正確的簽名。"""
        # 測試 get_local_now_naive 簽名
        sig = inspect.signature(get_local_now_naive)
        assert len(sig.parameters) == 0  # 無參數

        # 測試 get_utc_timestamp 簽名
        sig = inspect.signature(get_utc_timestamp)
        assert len(sig.parameters) == 0  # 無參數

    def test_imported_functions_return_expected_types(self):
        """測試導入的函數返回預期類型。"""
        # 測試 get_local_now_naive 返回類型
        result = get_local_now_naive()
        assert isinstance(result, datetime)

        # 測試 get_utc_timestamp 返回類型
        result = get_utc_timestamp()
        assert isinstance(result, str)

    def test_taiwan_timezone_consistency_across_imports(self):
        """測試台灣時區在不同導入中的一致性。"""
        assert tz1 is tz2
        assert id(tz1) == id(tz2)


if __name__ == "__main__":
    pytest.main([__file__])
