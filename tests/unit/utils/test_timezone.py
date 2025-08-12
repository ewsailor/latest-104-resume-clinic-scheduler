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
    convert_local_to_utc,
    convert_utc_to_local,
    format_datetime_for_display,
    get_local_now,
    get_local_now_naive,
    get_utc_timestamp,
    local_to_utc,
    now_local,
    now_utc,
    parse_datetime_from_display,
    utc_to_local,
)


class TestTimezoneModule:
    """時區模組測試類別。"""

    def test_taiwan_timezone_constant(self):
        """測試台灣時區常數。"""
        # 驗證台灣時區設定正確 (UTC+8)
        assert TAIWAN_TIMEZONE == timezone(timedelta(hours=8))
        assert TAIWAN_TIMEZONE.utcoffset(datetime.now()) == timedelta(hours=8)

    def test_get_local_now(self):
        """測試取得當前本地時間。"""
        # 執行測試
        local_now = get_local_now()

        # 驗證結果
        assert isinstance(local_now, datetime)
        assert local_now.tzinfo == TAIWAN_TIMEZONE
        assert local_now.tzinfo.utcoffset(local_now) == timedelta(hours=8)

    def test_get_local_now_naive(self):
        """測試取得當前本地時間（無時區資訊）。"""
        # 執行測試
        local_now_naive = get_local_now_naive()

        # 驗證結果
        assert isinstance(local_now_naive, datetime)
        assert local_now_naive.tzinfo is None

    @pytest.mark.parametrize(
        "input_dt,expected",
        [
            # 測試 UTC 時間
            (
                datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                "2024-01-01 20:00:00",  # UTC+8
            ),
            # 測試台灣時間
            (
                datetime(2024, 1, 1, 20, 0, 0, tzinfo=TAIWAN_TIMEZONE),
                "2024-01-01 20:00:00",
            ),
            # 測試無時區資訊的時間（假設為 UTC）
            (
                datetime(2024, 1, 1, 12, 0, 0),
                "2024-01-01 20:00:00",  # 假設為 UTC，轉換為台灣時間
            ),
        ],
    )
    def test_format_datetime_for_display(self, input_dt, expected):
        """測試格式化日期時間為顯示字串。"""
        # 執行測試
        result = format_datetime_for_display(input_dt)

        # 驗證結果
        assert result == expected

    def test_format_datetime_for_display_none(self):
        """測試格式化 None 值。"""
        # 執行測試
        result = format_datetime_for_display(None)

        # 驗證結果
        assert result is None

    @pytest.mark.parametrize(
        "display_str,expected_utc",
        [
            # 測試有效的日期時間字串
            (
                "2024-01-01 20:00:00",
                datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),  # 台灣時間轉 UTC
            ),
            # 測試邊界值
            (
                "2024-12-31 23:59:59",
                datetime(2024, 12, 31, 15, 59, 59, tzinfo=timezone.utc),
            ),
        ],
    )
    def test_parse_datetime_from_display_success(self, display_str, expected_utc):
        """測試成功解析日期時間字串。"""
        # 執行測試
        result = parse_datetime_from_display(display_str)

        # 驗證結果
        assert result is not None
        assert result.tzinfo == timezone.utc
        assert result == expected_utc

    @pytest.mark.parametrize(
        "display_str",
        [
            None,
            "",
            "invalid",
            "2024-13-01 20:00:00",  # 無效月份
            "2024-01-32 20:00:00",  # 無效日期
            "2024-01-01 25:00:00",  # 無效小時
        ],
    )
    def test_parse_datetime_from_display_failure(self, display_str):
        """測試解析日期時間字串失敗。"""
        # 執行測試
        result = parse_datetime_from_display(display_str)

        # 驗證結果
        assert result is None

    @pytest.mark.parametrize(
        "utc_dt,expected_local",
        [
            # 測試 UTC 時間轉本地時間
            (
                datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                datetime(2024, 1, 1, 20, 0, 0, tzinfo=TAIWAN_TIMEZONE),
            ),
            # 測試無時區資訊的時間（假設為 UTC）
            (
                datetime(2024, 1, 1, 12, 0, 0),
                datetime(2024, 1, 1, 20, 0, 0, tzinfo=TAIWAN_TIMEZONE),
            ),
        ],
    )
    def test_convert_utc_to_local_success(self, utc_dt, expected_local):
        """測試成功轉換 UTC 時間為本地時間。"""
        # 執行測試
        result = convert_utc_to_local(utc_dt)

        # 驗證結果
        assert result is not None
        assert result.tzinfo == TAIWAN_TIMEZONE
        assert result == expected_local

    def test_convert_utc_to_local_none(self):
        """測試轉換 None 值。"""
        # 執行測試
        result = convert_utc_to_local(None)

        # 驗證結果
        assert result is None

    @pytest.mark.parametrize(
        "local_dt,expected_utc",
        [
            # 測試本地時間轉 UTC 時間
            (
                datetime(2024, 1, 1, 20, 0, 0, tzinfo=TAIWAN_TIMEZONE),
                datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            ),
            # 測試無時區資訊的時間（假設為本地時間）
            (
                datetime(2024, 1, 1, 20, 0, 0),
                datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            ),
        ],
    )
    def test_convert_local_to_utc_success(self, local_dt, expected_utc):
        """測試成功轉換本地時間為 UTC 時間。"""
        # 執行測試
        result = convert_local_to_utc(local_dt)

        # 驗證結果
        assert result is not None
        assert result.tzinfo == timezone.utc
        assert result == expected_utc

    def test_convert_local_to_utc_none(self):
        """測試轉換 None 值。"""
        # 執行測試
        result = convert_local_to_utc(None)

        # 驗證結果
        assert result is None

    def test_get_utc_timestamp(self):
        """測試取得 UTC 時間戳記。"""
        # 模擬固定的 UTC 時間
        with patch("app.utils.timezone.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now

            # 執行測試
            result = get_utc_timestamp()

            # 驗證結果
            assert result == "2024-01-01T12:00:00Z"
            assert isinstance(result, str)

    def test_now_local_alias(self):
        """測試 now_local 別名函數。"""
        # 執行測試
        result = now_local()

        # 驗證結果
        assert isinstance(result, datetime)
        assert result.tzinfo == TAIWAN_TIMEZONE

    def test_now_utc_alias(self):
        """測試 now_utc 別名函數。"""
        # 模擬固定的 UTC 時間
        with patch("app.utils.timezone.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now

            # 執行測試
            result = now_utc()

            # 驗證結果
            assert result == mock_now
            assert result.tzinfo == timezone.utc

    def test_utc_to_local_alias(self):
        """測試 utc_to_local 別名函數。"""
        # 準備測試資料
        utc_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        expected_local = datetime(2024, 1, 1, 20, 0, 0, tzinfo=TAIWAN_TIMEZONE)

        # 執行測試
        result = utc_to_local(utc_dt)

        # 驗證結果
        assert result == expected_local

    def test_local_to_utc_alias(self):
        """測試 local_to_utc 別名函數。"""
        # 準備測試資料
        local_dt = datetime(2024, 1, 1, 20, 0, 0, tzinfo=TAIWAN_TIMEZONE)
        expected_utc = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # 執行測試
        result = local_to_utc(local_dt)

        # 驗證結果
        assert result == expected_utc

    def test_edge_cases(self):
        """測試邊界情況。"""
        # 測試夏令時間邊界（如果適用）
        # 測試跨年邊界
        # 測試閏年

        # 跨年測試
        local_dt = datetime(2023, 12, 31, 23, 59, 59, tzinfo=TAIWAN_TIMEZONE)
        utc_dt = convert_local_to_utc(local_dt)
        assert utc_dt == datetime(2023, 12, 31, 15, 59, 59, tzinfo=timezone.utc)

        # 閏年測試
        local_dt = datetime(2024, 2, 29, 12, 0, 0, tzinfo=TAIWAN_TIMEZONE)
        utc_dt = convert_local_to_utc(local_dt)
        assert utc_dt == datetime(2024, 2, 29, 4, 0, 0, tzinfo=timezone.utc)

    def test_timezone_conversion_roundtrip(self):
        """測試時區轉換的往返一致性。"""
        # 準備測試資料
        original_utc = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # UTC -> Local -> UTC
        local_dt = convert_utc_to_local(original_utc)
        result_utc = convert_local_to_utc(local_dt)

        # 驗證往返一致性
        assert result_utc == original_utc

        # Local -> UTC -> Local
        original_local = datetime(2024, 1, 1, 20, 0, 0, tzinfo=TAIWAN_TIMEZONE)
        utc_dt = convert_local_to_utc(original_local)
        result_local = convert_utc_to_local(utc_dt)

        # 驗證往返一致性
        assert result_local == original_local

    def test_format_and_parse_roundtrip(self):
        """測試格式化和解析的往返一致性。"""
        # 準備測試資料
        original_utc = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # UTC -> Display -> UTC
        display_str = format_datetime_for_display(original_utc)
        result_utc = parse_datetime_from_display(display_str)

        # 驗證往返一致性
        assert result_utc == original_utc

    def test_logging_coverage(self):
        """測試日誌記錄覆蓋率。"""
        # 測試 format_datetime_for_display 的警告日誌
        with patch("app.utils.timezone.logger") as mock_logger:
            naive_dt = datetime(2024, 1, 1, 12, 0, 0)  # 無時區資訊
            format_datetime_for_display(naive_dt)
            mock_logger.warning.assert_called_once()

        # 測試 parse_datetime_from_display 的錯誤日誌
        with patch("app.utils.timezone.logger") as mock_logger:
            parse_datetime_from_display("invalid")
            mock_logger.error.assert_called_once()

        # 測試 get_utc_timestamp 的調試日誌
        with patch("app.utils.timezone.logger") as mock_logger:
            with patch("app.utils.timezone.datetime") as mock_datetime:
                mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
                mock_datetime.now.return_value = mock_now
                get_utc_timestamp()
                assert mock_logger.debug.call_count == 2  # called 和 success
