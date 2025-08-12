"""
時區工具模組測試。

測試時區轉換和本地時間處理的實用函數。
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

# ===== 本地模組 =====
from app.utils.timezone import (
    TAIWAN_TIMEZONE,
    get_local_now_naive,
    get_utc_timestamp,
)


class TestTimezoneModule:
    """時區模組測試類別。"""

    def test_taiwan_timezone_constant(self):
        """測試台灣時區常數。"""
        # 驗證台灣時區設定正確 (UTC+8)
        assert TAIWAN_TIMEZONE == timezone(timedelta(hours=8))
        assert TAIWAN_TIMEZONE.utcoffset(datetime.now()) == timedelta(hours=8)

    def test_get_local_now_naive(self):
        """測試取得當前本地時間（無時區資訊）。"""
        # 執行測試
        local_now_naive = get_local_now_naive()

        # 驗證結果
        assert isinstance(local_now_naive, datetime)
        assert local_now_naive.tzinfo is None

    def test_get_utc_timestamp(self):
        """測試取得 UTC 時間戳記。"""
        # 執行測試
        timestamp = get_utc_timestamp()

        # 驗證結果
        assert isinstance(timestamp, str)
        # 檢查格式：YYYY-MM-DDTHH:MM:SSZ
        assert len(timestamp) == 20
        assert timestamp.endswith('Z')
        assert 'T' in timestamp

    def test_get_utc_timestamp_format(self):
        """測試 UTC 時間戳記格式。"""
        # 執行測試
        timestamp = get_utc_timestamp()

        # 驗證格式
        parts = timestamp.split('T')
        assert len(parts) == 2

        date_part = parts[0]
        time_part = parts[1].rstrip('Z')

        # 檢查日期格式：YYYY-MM-DD
        assert len(date_part) == 10
        assert date_part.count('-') == 2

        # 檢查時間格式：HH:MM:SS
        assert len(time_part) == 8
        assert time_part.count(':') == 2

    @patch('app.utils.timezone.logger')
    def test_get_utc_timestamp_logging(self, mock_logger):
        """測試 UTC 時間戳記的日誌記錄。"""
        # 設定 logger 為 DEBUG 級別
        mock_logger.isEnabledFor.return_value = True

        # 執行測試
        timestamp = get_utc_timestamp()

        # 驗證日誌記錄
        mock_logger.debug.assert_called_once()
        log_message = mock_logger.debug.call_args[0][0]
        assert "生成 UTC 時間戳記" in log_message
        assert timestamp in log_message
