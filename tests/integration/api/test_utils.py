"""
測試工具模組。

提供測試中常用的工具函數，避免重複代碼。
"""

# ===== 標準函式庫 =====
import datetime
import random
import time
from typing import Tuple


def generate_unique_time_slot(
    days_offset: int = 365,
    hour_range: int = 20,
    minute_range: int = 55,
    hour_start: int = 1,
    minute_start: int = 1,
) -> Tuple[str, str, str]:
    """
    生成唯一的時段時間，避免測試重疊。

    Args:
        days_offset: 未來天數偏移，預設 365 天
        hour_range: 小時範圍，預設 20（1-20 小時）
        minute_range: 分鐘範圍，預設 55（1-55 分鐘）
        hour_start: 小時起始值，預設 1
        minute_start: 分鐘起始值，預設 1

    Returns:
        Tuple[str, str, str]: (date, start_time, end_time)
    """
    # 使用納秒級時間戳 + 隨機數 + 進程ID確保唯一性
    timestamp = int(time.time() * 1000000000)  # 納秒級時間戳
    random_offset = random.randint(0, 999999)  # 隨機偏移
    process_id = hash(str(time.time())) % 10000  # 進程相關的唯一ID
    unique_id = timestamp + random_offset + process_id

    # 計算未來日期
    future_date = datetime.date.today() + datetime.timedelta(days=days_offset)

    # 使用更大的模數範圍，並加入隨機元素
    hour = (unique_id % hour_range) + hour_start
    minute = (unique_id % minute_range) + minute_start

    # 確保小時在 24 小時制範圍內
    hour = hour % 24

    # 生成開始和結束時間
    start_time = f"{hour:02d}:{minute:02d}:00"

    # 計算結束時間，處理分鐘溢出
    if (minute + 30) < 60:
        end_time = f"{hour:02d}:{(minute + 30):02d}:00"
    else:
        end_hour = (hour + 1) % 24
        end_minute = (minute + 30) - 60
        end_time = f"{end_hour:02d}:{end_minute:02d}:00"

    return future_date.strftime("%Y-%m-%d"), start_time, end_time


def generate_multiple_time_slots(
    count: int = 2,
    days_offset: int = 365,
    hour_range: int = 20,
    minute_range: int = 55,
    hour_start: int = 1,
    minute_start: int = 1,
) -> list[Tuple[str, str, str]]:
    """
    生成多個唯一的時段時間。

    Args:
        count: 要生成的時段數量
        days_offset: 未來天數偏移，預設 365 天
        hour_range: 小時範圍，預設 20（1-20 小時）
        minute_range: 分鐘範圍，預設 55（1-55 分鐘）
        hour_start: 小時起始值，預設 1
        minute_start: 分鐘起始值，預設 1

    Returns:
        list[Tuple[str, str, str]]: 時段列表，每個元素為 (date, start_time, end_time)
    """
    slots = []
    base_timestamp = int(time.time() * 1000000)

    for i in range(count):
        # 為每個時段添加不同的偏移
        timestamp = base_timestamp + (i * 1000000)  # 每個時段間隔 1 秒
        random_offset = random.randint(0, 999999)
        unique_id = timestamp + random_offset

        # 計算未來日期
        future_date = datetime.date.today() + datetime.timedelta(days=days_offset)

        # 使用不同的模數計算，確保時段不重疊
        hour = (unique_id % hour_range) + hour_start + i  # 每個時段小時遞增
        minute = (unique_id % minute_range) + minute_start

        # 確保小時在 24 小時制範圍內
        hour = hour % 24

        # 生成開始和結束時間
        start_time = f"{hour:02d}:{minute:02d}:00"

        # 計算結束時間，處理分鐘溢出
        if (minute + 30) < 60:
            end_time = f"{hour:02d}:{(minute + 30):02d}:00"
        else:
            end_hour = (hour + 1) % 24
            end_minute = (minute + 30) - 60
            end_time = f"{end_hour:02d}:{end_minute:02d}:00"

        slots.append((future_date.strftime("%Y-%m-%d"), start_time, end_time))

    return slots
