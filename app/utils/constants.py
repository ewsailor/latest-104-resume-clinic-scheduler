"""常數定義模組。

集中管理系統中使用的常數，包括日期格式、週名稱、錯誤訊息等。
"""


class WeekdayNames:
    """週名稱常數。"""

    # Python datetime.weekday() 對應 (週一=0, 週日=6)
    CHINESE_WEEKDAYS: list[str] = [
        '週一',
        '週二',
        '週三',
        '週四',
        '週五',
        '週六',
        '週日',
    ]

    # 簡短版本
    CHINESE_WEEKDAYS_SHORT: list[str] = ['一', '二', '三', '四', '五', '六', '日']

    # JavaScript Date.getDay() 對應 (週日=0, 週六=6)
    CHINESE_WEEKDAYS_JS_ORDER: list[str] = [
        '週日',
        '週一',
        '週二',
        '週三',
        '週四',
        '週五',
        '週六',
    ]


class DateTimeFormats:
    """日期時間格式常數。"""

    DATE_FORMAT: str = "%Y/%m/%d"
    TIME_FORMAT: str = "%H:%M"
    DATETIME_FORMAT: str = "%Y/%m/%d %H:%M"

    # 日期分隔符
    DATE_SEPARATOR: str = "/"
    TIME_SEPARATOR: str = ":"
    SCHEDULE_SEPARATOR: str = "-"
    SCHEDULE_RANGE_SEPARATOR: str = "~"


class ScheduleConstants:
    """時段相關常數。"""

    # 時段顯示格式模板
    DATE_WITH_WEEKDAY_TEMPLATE: str = "{date}（{weekday}）"
    TIME_RANGE_TEMPLATE: str = "{start_time}{separator}{end_time}"
    FULL_SCHEDULE_TEMPLATE: str = "{date_with_weekday} {time_range}"


class ErrorMessages:
    """錯誤訊息常數。"""

    SCHEDULE_OVERLAP_TEMPLATE: str = (
        "您正輸入的時段，和您之前曾輸入的「{overlapping_info}」時段重複或重疊，請重新輸入"
    )
