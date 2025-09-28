"""時區處理工具測試。"""

# ===== 標準函式庫 =====
from datetime import datetime, timezone
from unittest.mock import patch

# ===== 本地模組 =====
from app.utils.timezone import TAIWAN_TIMEZONE, get_local_now_naive, get_utc_timestamp


@patch('app.utils.timezone.datetime')
def test_get_local_now_naive(mock_datetime):
    """測試取得台灣時區的本地時間。"""
    # GIVEN：建立一個模擬的台灣時區時間，2024年1月15日 12:30:45
    mock_taiwan_time = datetime(2024, 1, 15, 12, 30, 45, tzinfo=TAIWAN_TIMEZONE)
    # 設定 mock_datetime.now() 返回這個模擬時間
    mock_datetime.now.return_value = mock_taiwan_time

    # WHEN：呼叫函數取得本地時間
    result = get_local_now_naive()

    # THEN：確認返回正確的時間且無時區資訊
    expected_time = datetime(2024, 1, 15, 12, 30, 45)
    assert result == expected_time

    # THEN：返回的時間物件沒有時區資訊，即 tzinfo 是 None
    assert result.tzinfo is None


@patch('app.utils.timezone.datetime')
def test_get_utc_timestamp(mock_datetime):
    """測試取得 UTC 時間戳記字串。"""
    # GIVEN：建立一個模擬的 UTC 時間，2024年1月15日 04:30:45 UTC
    mock_utc_time = datetime(2024, 1, 15, 4, 30, 45, tzinfo=timezone.utc)
    # 設定 mock_datetime.now() 返回這個模擬的 UTC 時間
    mock_datetime.now.return_value = mock_utc_time

    # WHEN：呼叫函數取得 UTC 時間戳記
    result = get_utc_timestamp()

    # THEN：確認返回 ISO 格式時間戳記，ISO 8601 格式：YYYY-MM-DDTHH:MM:SSZ
    expected_timestamp = "2024-01-15T04:30:45Z"
    assert result == expected_timestamp

    # THEN：字串結尾是 'Z'，表示 UTC 時區
    assert result.endswith('Z')
