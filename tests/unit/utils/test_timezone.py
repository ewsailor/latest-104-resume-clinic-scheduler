"""
時區處理工具測試。

測試時區處理工具模組的功能。
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

# ===== 標準函式庫 =====
import pytest

# ===== 本地模組 =====
from app.utils.timezone import TAIWAN_TIMEZONE, get_local_now_naive, get_utc_timestamp


# ===== 測試設定 =====
class TestTimezone:
    """時區處理工具測試類別。"""

    def test_taiwan_timezone_constant(self):
        """測試台灣時區常數。"""
        assert TAIWAN_TIMEZONE is not None
        assert isinstance(TAIWAN_TIMEZONE, timezone)
        assert TAIWAN_TIMEZONE.utcoffset(None) == timedelta(hours=8)

    def test_taiwan_timezone_offset(self):
        """測試台灣時區偏移量。"""
        # 台灣時區應該是 UTC+8
        expected_offset = timedelta(hours=8)
        assert TAIWAN_TIMEZONE.utcoffset(None) == expected_offset

    @patch('app.utils.timezone.datetime')
    def test_get_local_now_naive(self, mock_datetime):
        """測試取得本地時間（無時區資訊）。"""
        # 模擬台灣時間
        mock_taiwan_time = datetime(2024, 1, 15, 12, 30, 45, tzinfo=TAIWAN_TIMEZONE)
        mock_datetime.now.return_value = mock_taiwan_time

        result = get_local_now_naive()

        # 驗證結果
        assert result == datetime(2024, 1, 15, 12, 30, 45)  # 無時區資訊
        assert result.tzinfo is None
        mock_datetime.now.assert_called_once_with(TAIWAN_TIMEZONE)

    @patch('app.utils.timezone.datetime')
    def test_get_local_now_naive_different_time(self, mock_datetime):
        """測試取得本地時間 - 不同時間。"""
        # 模擬不同的台灣時間
        mock_taiwan_time = datetime(2024, 12, 25, 23, 59, 59, tzinfo=TAIWAN_TIMEZONE)
        mock_datetime.now.return_value = mock_taiwan_time

        result = get_local_now_naive()

        # 驗證結果
        assert result == datetime(2024, 12, 25, 23, 59, 59)
        assert result.tzinfo is None

    @patch('app.utils.timezone.datetime')
    def test_get_utc_timestamp(self, mock_datetime):
        """測試取得 UTC 時間戳記。"""
        # 模擬 UTC 時間
        mock_utc_time = datetime(2024, 1, 15, 4, 30, 45, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_utc_time

        result = get_utc_timestamp()

        # 驗證結果
        assert result == "2024-01-15T04:30:45Z"
        mock_datetime.now.assert_called_once_with(timezone.utc)

    @patch('app.utils.timezone.datetime')
    def test_get_utc_timestamp_different_time(self, mock_datetime):
        """測試取得 UTC 時間戳記 - 不同時間。"""
        # 模擬不同的 UTC 時間
        mock_utc_time = datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_utc_time

        result = get_utc_timestamp()

        # 驗證結果
        assert result == "2024-12-31T23:59:59Z"

    @patch('app.utils.timezone.datetime')
    def test_get_utc_timestamp_with_microseconds(self, mock_datetime):
        """測試取得 UTC 時間戳記 - 包含微秒。"""
        # 模擬包含微秒的 UTC 時間
        mock_utc_time = datetime(2024, 1, 15, 4, 30, 45, 123456, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_utc_time

        result = get_utc_timestamp()

        # 驗證結果（微秒會被 strftime 忽略）
        assert result == "2024-01-15T04:30:45Z"

    @patch('app.utils.timezone.logger')
    @patch('app.utils.timezone.datetime')
    def test_get_utc_timestamp_with_debug_logging(self, mock_datetime, mock_logger):
        """測試取得 UTC 時間戳記 - 除錯日誌。"""
        # 設置 logger 為 DEBUG 級別
        mock_logger.isEnabledFor.return_value = True

        # 模擬 UTC 時間
        mock_utc_time = datetime(2024, 1, 15, 4, 30, 45, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_utc_time

        result = get_utc_timestamp()

        # 驗證結果
        assert result == "2024-01-15T04:30:45Z"

        # 驗證日誌調用
        mock_logger.isEnabledFor.assert_called_once()
        mock_logger.debug.assert_called_once_with(
            "生成 UTC 時間戳記: 2024-01-15T04:30:45Z"
        )

    @patch('app.utils.timezone.logger')
    @patch('app.utils.timezone.datetime')
    def test_get_utc_timestamp_without_debug_logging(self, mock_datetime, mock_logger):
        """測試取得 UTC 時間戳記 - 無除錯日誌。"""
        # 設置 logger 不為 DEBUG 級別
        mock_logger.isEnabledFor.return_value = False

        # 模擬 UTC 時間
        mock_utc_time = datetime(2024, 1, 15, 4, 30, 45, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_utc_time

        result = get_utc_timestamp()

        # 驗證結果
        assert result == "2024-01-15T04:30:45Z"

        # 驗證日誌調用
        mock_logger.isEnabledFor.assert_called_once()
        mock_logger.debug.assert_not_called()

    def test_taiwan_timezone_consistency(self):
        """測試台灣時區一致性。"""
        # 驗證台灣時區在不同時間點的偏移量都是一致的
        test_dates = [
            datetime(2024, 1, 1),  # 冬季
            datetime(2024, 6, 1),  # 夏季
            datetime(2024, 12, 31),  # 年末
        ]

        for test_date in test_dates:
            offset = TAIWAN_TIMEZONE.utcoffset(test_date)
            assert offset == timedelta(hours=8)

    def test_taiwan_timezone_dst_handling(self):
        """測試台灣時區夏令時間處理。"""
        # 台灣不使用夏令時間，所以偏移量應該始終是 +8
        # 測試不同月份
        months = [1, 3, 6, 9, 12]

        for month in months:
            test_date = datetime(2024, month, 15)
            offset = TAIWAN_TIMEZONE.utcoffset(test_date)
            assert offset == timedelta(hours=8)

    def test_timezone_comparison(self):
        """測試時區比較。"""
        # 創建其他時區進行比較
        utc_plus_8 = timezone(timedelta(hours=8))
        utc_plus_9 = timezone(timedelta(hours=9))

        # 台灣時區應該等於 UTC+8
        assert TAIWAN_TIMEZONE.utcoffset(None) == utc_plus_8.utcoffset(None)

        # 台灣時區不應該等於 UTC+9
        assert TAIWAN_TIMEZONE.utcoffset(None) != utc_plus_9.utcoffset(None)

    def test_get_local_now_naive_timezone_removal(self):
        """測試取得本地時間時區資訊移除。"""
        with patch('app.utils.timezone.datetime') as mock_datetime:
            # 模擬帶時區資訊的台灣時間
            mock_taiwan_time = datetime(2024, 1, 15, 12, 30, 45, tzinfo=TAIWAN_TIMEZONE)
            mock_datetime.now.return_value = mock_taiwan_time

            result = get_local_now_naive()

            # 驗證時區資訊被移除
            assert result.tzinfo is None
            assert result.replace(tzinfo=TAIWAN_TIMEZONE) == mock_taiwan_time

    def test_get_utc_timestamp_format(self):
        """測試 UTC 時間戳記格式。"""
        with patch('app.utils.timezone.datetime') as mock_datetime:
            # 模擬 UTC 時間
            mock_utc_time = datetime(2024, 1, 15, 4, 30, 45, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_utc_time

            result = get_utc_timestamp()

            # 驗證格式
            assert result.endswith('Z')
            assert 'T' in result
            assert len(result) == 20  # YYYY-MM-DDTHH:MM:SSZ
            assert result.count('-') == 2
            assert result.count(':') == 2


if __name__ == "__main__":
    pytest.main([__file__])
