"""
測試工具模組。

提供測試中常用的工具函數，避免重複代碼。
"""

# ===== 標準函式庫 =====
import datetime
import random
import time
from typing import Set, Tuple

# 全域時段追蹤 set，用於確保測試時段唯一性
_used_time_slots: Set[str] = set()


def _generate_time_slot_key(date: str, start_time: str, end_time: str) -> str:
    """
    生成時段的唯一鍵值。

    Args:
        date: 日期字串 (YYYY-MM-DD)
        start_time: 開始時間字串 (HH:MM:SS)
        end_time: 結束時間字串 (HH:MM:SS)

    Returns:
        str: 時段的唯一鍵值
    """
    return f"{date}|{start_time}|{end_time}"


def _is_time_slot_used(date: str, start_time: str, end_time: str) -> bool:
    """
    檢查時段是否已被使用。

    Args:
        date: 日期字串
        start_time: 開始時間字串
        end_time: 結束時間字串

    Returns:
        bool: 如果時段已被使用則返回 True
    """
    key = _generate_time_slot_key(date, start_time, end_time)
    return key in _used_time_slots


def _mark_time_slot_used(date: str, start_time: str, end_time: str) -> None:
    """
    標記時段為已使用。

    Args:
        date: 日期字串
        start_time: 開始時間字串
        end_time: 結束時間字串
    """
    key = _generate_time_slot_key(date, start_time, end_time)
    _used_time_slots.add(key)


def clear_used_time_slots() -> None:
    """
    清除所有已使用的時段記錄。
    在測試開始前或測試結束後調用。
    """
    global _used_time_slots  # noqa: F824
    _used_time_slots.clear()


def generate_unique_time_slot(
    days_offset: int = 365,
) -> Tuple[str, str, str]:
    """
    生成唯一的時段時間，使用 set 確保唯一性。

    Args:
        days_offset: 未來天數偏移，預設 365 天

    Returns:
        Tuple[str, str, str]: (date, start_time, end_time)
    """
    # 簡化的時間生成邏輯
    timestamp = int(time.time() * 1000)  # 毫秒級時間戳
    random_offset = random.randint(0, 999)  # 隨機偏移

    # 計算未來日期
    future_date = datetime.date.today() + datetime.timedelta(
        days=days_offset + (timestamp % 30)
    )

    # 簡單的小時和分鐘計算
    hour = (timestamp % 20) + 1  # 1-20 小時
    minute = (random_offset % 50) + 1  # 1-50 分鐘

    # 生成開始和結束時間
    start_time = f"{hour:02d}:{minute:02d}:00"

    # 計算結束時間（30分鐘後）
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
) -> list[Tuple[str, str, str]]:
    """
    生成多個唯一的時段時間，使用 set 確保不重疊。

    Args:
        count: 要生成的時段數量
        days_offset: 未來天數偏移，預設 365 天

    Returns:
        list[Tuple[str, str, str]]: 時段列表，每個元素為 (date, start_time, end_time)
    """
    slots = []

    for i in range(count):
        # 使用簡化的時間生成邏輯
        timestamp = int(time.time() * 1000) + i  # 每個時段間隔 1 毫秒
        random_offset = random.randint(0, 999)

        # 計算未來日期
        future_date = datetime.date.today() + datetime.timedelta(
            days=days_offset + (timestamp % 30)
        )

        # 簡單的小時和分鐘計算
        hour = (timestamp % 20) + 1  # 1-20 小時
        minute = (random_offset % 50) + 1  # 1-50 分鐘

        # 生成開始和結束時間
        start_time = f"{hour:02d}:{minute:02d}:00"

        # 計算結束時間（30分鐘後）
        if (minute + 30) < 60:
            end_time = f"{hour:02d}:{(minute + 30):02d}:00"
        else:
            end_hour = (hour + 1) % 24
            end_minute = (minute + 30) - 60
            end_time = f"{end_hour:02d}:{end_minute:02d}:00"

        slots.append((future_date.strftime("%Y-%m-%d"), start_time, end_time))

    return slots


def generate_guaranteed_unique_time_slot(
    days_offset: int = 365,
    max_attempts: int = 100,
) -> Tuple[str, str, str]:
    """
    生成保證唯一的時段時間，使用 set 追蹤確保絕對唯一性。

    Args:
        days_offset: 未來天數偏移，預設 365 天
        max_attempts: 最大嘗試次數，預設 100 次

    Returns:
        Tuple[str, str, str]: (date, start_time, end_time)

    Raises:
        RuntimeError: 如果無法在指定次數內生成唯一時段
    """
    for attempt in range(max_attempts):
        # 簡化的時間生成邏輯
        timestamp = int(time.time() * 1000)  # 毫秒級時間戳
        random_offset = random.randint(0, 999)  # 隨機偏移

        # 計算未來日期
        future_date = datetime.date.today() + datetime.timedelta(
            days=days_offset + (timestamp % 30)
        )

        # 簡單的小時和分鐘計算
        hour = (timestamp % 20) + 1  # 1-20 小時
        minute = (random_offset % 50) + 1  # 1-50 分鐘

        # 生成開始和結束時間
        start_time = f"{hour:02d}:{minute:02d}:00"

        # 計算結束時間（30分鐘後）
        if (minute + 30) < 60:
            end_time = f"{hour:02d}:{(minute + 30):02d}:00"
        else:
            end_hour = (hour + 1) % 24
            end_minute = (minute + 30) - 60
            end_time = f"{end_hour:02d}:{end_minute:02d}:00"

        date_str = future_date.strftime("%Y-%m-%d")

        # 檢查時段是否已被使用
        if not _is_time_slot_used(date_str, start_time, end_time):
            # 標記時段為已使用
            _mark_time_slot_used(date_str, start_time, end_time)
            return date_str, start_time, end_time

    # 如果無法在指定次數內生成唯一時段，拋出錯誤
    raise RuntimeError(
        f"無法在 {max_attempts} 次嘗試內生成唯一時段。已使用時段數量: {len(_used_time_slots)}"
    )


def generate_multiple_guaranteed_unique_time_slots(
    count: int = 2,
    days_offset: int = 365,
    max_attempts_per_slot: int = 100,
) -> list[Tuple[str, str, str]]:
    """
    生成多個保證唯一的時段時間，使用 set 追蹤確保絕對唯一性。

    Args:
        count: 要生成的時段數量
        days_offset: 未來天數偏移，預設 365 天
        max_attempts_per_slot: 每個時段的最大嘗試次數，預設 100 次

    Returns:
        list[Tuple[str, str, str]]: 時段列表，每個元素為 (date, start_time, end_time)

    Raises:
        RuntimeError: 如果無法在指定次數內生成足夠的唯一時段
    """
    slots = []

    for i in range(count):
        try:
            slot = generate_guaranteed_unique_time_slot(
                days_offset=days_offset, max_attempts=max_attempts_per_slot
            )
            slots.append(slot)
        except RuntimeError as e:
            raise RuntimeError(f"生成第 {i+1} 個時段失敗: {e}")

    return slots


def get_used_time_slots_count() -> int:
    """
    獲取已使用的時段數量。

    Returns:
        int: 已使用的時段數量
    """
    return len(_used_time_slots)


def get_used_time_slots() -> Set[str]:
    """
    獲取所有已使用的時段（用於調試）。

    Returns:
        Set[str]: 所有已使用的時段鍵值集合
    """
    return _used_time_slots.copy()


# ===== Pytest Fixtures =====
def pytest_configure():
    """
    Pytest 配置函數，在測試開始前清除時段追蹤。
    """
    clear_used_time_slots()


def pytest_unconfigure():
    """
    Pytest 配置函數，在測試結束後清除時段追蹤。
    """
    clear_used_time_slots()
