"""時區處理工具測試。"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.utils.timezone import TAIWAN_TIMEZONE, get_local_now_naive, get_utc_timestamp


def test_taiwan_timezone():
    """測試台灣時區常數。"""
    # GIVEN：台灣時區常數已定義

    # WHEN：檢查時區屬性
    is_not_none = TAIWAN_TIMEZONE is not None
    is_timezone = isinstance(TAIWAN_TIMEZONE, timezone)
    utc_offset = TAIWAN_TIMEZONE.utcoffset(None)

    # THEN：確認時區設定正確
    assert is_not_none
    assert is_timezone
    assert utc_offset == timedelta(hours=8)


@patch('app.utils.timezone.datetime')
def test_get_local_now_naive(mock_datetime):
    """測試取得本地時間。"""
    # GIVEN：模擬台灣時區的當前時間
    mock_taiwan_time = datetime(2024, 1, 15, 12, 30, 45, tzinfo=TAIWAN_TIMEZONE)
    mock_datetime.now.return_value = mock_taiwan_time

    # WHEN：取得本地時間（無時區資訊）
    result = get_local_now_naive()

    # THEN：確認返回正確的時間且無時區資訊
    assert result == datetime(2024, 1, 15, 12, 30, 45)
    assert result.tzinfo is None


@patch('app.utils.timezone.datetime')
def test_get_utc_timestamp(mock_datetime):
    """測試取得 UTC 時間戳記。"""
    # GIVEN：模擬 UTC 時間
    mock_utc_time = datetime(2024, 1, 15, 4, 30, 45, tzinfo=timezone.utc)
    mock_datetime.now.return_value = mock_utc_time

    # WHEN：取得 UTC 時間戳記
    result = get_utc_timestamp()

    # THEN：確認返回正確的 ISO 格式時間戳記
    assert result == "2024-01-15T04:30:45Z"
    assert result.endswith('Z')
