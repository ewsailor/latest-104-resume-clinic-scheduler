"""
時間時段生成工具測試模組。

測試時間時段生成函數的唯一性和效能。
"""

# ===== 標準函式庫 =====
import time

# ===== 本地模組 =====
from tests.utils.test_utils import (
    clear_used_time_slots,
    generate_guaranteed_unique_time_slot,
    generate_multiple_guaranteed_unique_time_slots,
    get_used_time_slots,
    get_used_time_slots_count,
)

# ===== 第三方套件 =====


class TestTimeSlotGeneration:
    """時間時段生成測試類別。"""

    def setup_method(self):
        """每個測試方法執行前清除時段追蹤。"""
        clear_used_time_slots()

    def teardown_method(self):
        """每個測試方法執行後清除時段追蹤。"""
        clear_used_time_slots()

    def test_generate_single_unique_time_slot(self):
        """測試生成單一唯一時段。"""
        date, start_time, end_time = generate_guaranteed_unique_time_slot()

        # 驗證格式
        assert isinstance(date, str)
        assert isinstance(start_time, str)
        assert isinstance(end_time, str)

        # 驗證時間格式
        assert len(date) == 10  # YYYY-MM-DD
        assert len(start_time) == 8  # HH:MM:SS
        assert len(end_time) == 8  # HH:MM:SS

        # 驗證已記錄
        assert get_used_time_slots_count() == 1

    def test_generate_multiple_unique_time_slots(self):
        """測試生成多個唯一時段。"""
        count = 10
        slots = generate_multiple_guaranteed_unique_time_slots(count=count)

        # 驗證數量
        assert len(slots) == count

        # 驗證格式
        for date, start_time, end_time in slots:
            assert isinstance(date, str)
            assert isinstance(start_time, str)
            assert isinstance(end_time, str)

        # 驗證唯一性
        unique_slots = set(slots)
        assert len(unique_slots) == len(slots)

        # 驗證已記錄
        assert get_used_time_slots_count() == count

    def test_generate_50_unique_time_slots(self):
        """測試生成 50 個唯一時段。"""
        count = 50
        slots = []

        for i in range(count):
            date, start_time, end_time = generate_guaranteed_unique_time_slot()
            slots.append((date, start_time, end_time))

        # 驗證數量
        assert len(slots) == count

        # 驗證唯一性
        unique_slots = set(slots)
        assert len(unique_slots) == len(slots)

        # 驗證已記錄
        assert get_used_time_slots_count() == count

    def test_generate_100_unique_time_slots(self):
        """測試生成 100 個唯一時段。"""
        count = 100
        slots = []

        start_time_test = time.time()
        for i in range(count):
            date, start_time, end_time = generate_guaranteed_unique_time_slot()
            slots.append((date, start_time, end_time))
        end_time_test = time.time()

        # 驗證數量
        assert len(slots) == count

        # 驗證唯一性
        unique_slots = set(slots)
        assert len(unique_slots) == len(slots)

        # 驗證已記錄
        assert get_used_time_slots_count() == count

        # 驗證效能（應該在合理時間內完成）
        duration = end_time_test - start_time_test
        assert duration < 1.0  # 應該在 1 秒內完成
        print(f"生成 100 個時段耗時: {duration:.3f} 秒")

    def test_time_slot_uniqueness_across_multiple_calls(self):
        """測試多次調用時段唯一性。"""
        # 第一次調用
        slots1 = []
        for i in range(5):
            date, start_time, end_time = generate_guaranteed_unique_time_slot()
            slots1.append((date, start_time, end_time))

        # 第二次調用
        slots2 = []
        for i in range(5):
            date, start_time, end_time = generate_guaranteed_unique_time_slot()
            slots2.append((date, start_time, end_time))

        # 驗證兩次調用的時段都不重複
        all_slots = slots1 + slots2
        unique_slots = set(all_slots)
        assert len(unique_slots) == len(all_slots)

        # 驗證已記錄
        assert get_used_time_slots_count() == 10

    def test_time_slot_format_validation(self):
        """測試時段格式驗證。"""
        date, start_time, end_time = generate_guaranteed_unique_time_slot()

        # 驗證日期格式 (YYYY-MM-DD)
        date_parts = date.split('-')
        assert len(date_parts) == 3
        assert len(date_parts[0]) == 4  # 年份
        assert len(date_parts[1]) == 2  # 月份
        assert len(date_parts[2]) == 2  # 日期

        # 驗證時間格式 (HH:MM:SS)
        time_parts = start_time.split(':')
        assert len(time_parts) == 3
        assert len(time_parts[0]) == 2  # 小時
        assert len(time_parts[1]) == 2  # 分鐘
        assert len(time_parts[2]) == 2  # 秒

        # 驗證時間範圍
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        assert 1 <= hour <= 20  # 1-20 小時
        assert 1 <= minute <= 50  # 1-50 分鐘

    def test_used_time_slots_tracking(self):
        """測試已使用時段追蹤功能。"""
        # 生成幾個時段
        slots = []
        for i in range(3):
            date, start_time, end_time = generate_guaranteed_unique_time_slot()
            slots.append((date, start_time, end_time))

        # 驗證追蹤
        assert get_used_time_slots_count() == 3

        # 獲取已使用的時段
        used_slots = get_used_time_slots()
        assert len(used_slots) == 3

        # 驗證格式
        for slot in used_slots:
            assert '|' in slot  # 應該是 "date|start_time|end_time" 格式

    def test_clear_used_time_slots(self):
        """測試清除已使用時段功能。"""
        # 生成一些時段
        for i in range(5):
            generate_guaranteed_unique_time_slot()

        # 驗證已記錄
        assert get_used_time_slots_count() == 5

        # 清除記錄
        clear_used_time_slots()

        # 驗證已清除
        assert get_used_time_slots_count() == 0

        # 驗證可以重新生成
        date, start_time, end_time = generate_guaranteed_unique_time_slot()
        assert get_used_time_slots_count() == 1
