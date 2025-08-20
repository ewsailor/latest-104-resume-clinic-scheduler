"""
時段驗證器模組。

提供時段相關的驗證功能，包括日期、時間、重疊檢查等。
"""

import logging
from datetime import date, datetime, time
from typing import Any, List

from sqlalchemy import and_

from app.enums.models import UserRoleEnum
from app.models.schedule import Schedule
from app.schemas import ScheduleData
from app.utils.error_handler import (
    BusinessLogicError,
    ErrorCode,
    NotFoundError,
    format_schedule_overlap_error_message,
)
from app.utils.validators import ParameterValidator


class ScheduleValidator:
    """時段驗證器類別。"""

    def __init__(self):
        """初始化驗證器，設定日誌器。"""
        self.logger = logging.getLogger(__name__)

        # 休息時間設定
        self.REST_START_TIME = time(0, 0)  # 00:00
        self.REST_END_TIME = time(8, 0)  # 08:00

        # 其他限制
        self.MAX_NOTE_LENGTH = 265
        self.MAX_MONTHS_AHEAD = 3

    def validate_schedule_data(
        self, schedule_data: ScheduleData, skip_date_validation: bool = False
    ) -> None:
        """
        驗證單一時段資料。

        Args:
            schedule_data: 要驗證的時段資料

        Raises:
            ValueError: 當驗證失敗時
        """
        self.logger.debug(f"開始驗證時段資料: {schedule_data}")

        # 基本參數驗證
        self._validate_basic_parameters(schedule_data)

        # 日期驗證（可選跳過）
        if not skip_date_validation:
            self._validate_schedule_date(schedule_data.schedule_date)

        # 時間驗證
        self._validate_time_range(schedule_data.start_time, schedule_data.end_time)

        # 營業時間驗證
        self._validate_business_hours(schedule_data.start_time, schedule_data.end_time)

        # 備註驗證
        self._validate_note(schedule_data.note)

        self.logger.debug("時段資料驗證通過")

    def validate_schedules_list(
        self,
        schedules: List[ScheduleData],
        db: Any,
        check_overlap: bool = True,
        skip_date_validation: bool = False,
    ) -> None:
        """
        驗證時段列表。

        Args:
            schedules: 要驗證的時段列表
            db: 資料庫會話
            check_overlap: 是否檢查重疊

        Raises:
            ValueError: 當驗證失敗時
        """
        self.logger.info(f"開始驗證 {len(schedules)} 個時段")

        # 驗證列表參數
        ParameterValidator.validate_list(schedules, "schedules", ScheduleData)

        # 驗證每個時段
        for i, schedule_data in enumerate(schedules):
            try:
                self.validate_schedule_data(
                    schedule_data, skip_date_validation=skip_date_validation
                )
            except ValueError as e:
                raise ValueError(f"時段 {i+1} 驗證失敗: {str(e)}")

        # 檢查重疊（如果需要）
        if check_overlap:
            self._validate_schedule_overlaps(schedules, db)

        self.logger.info("所有時段驗證通過")

    def _validate_basic_parameters(self, schedule_data: ScheduleData) -> None:
        """驗證基本參數。"""
        # 驗證 giver_id
        ParameterValidator.validate_positive_int(schedule_data.giver_id, "giver_id")

        # 驗證 taker_id（如果提供）
        if schedule_data.taker_id is not None:
            ParameterValidator.validate_positive_int(schedule_data.taker_id, "taker_id")

    def _validate_schedule_date(self, schedule_date: date) -> None:
        """
        驗證時段日期。

        Args:
            schedule_date: 要驗證的日期

        Raises:
            ValueError: 當日期無效時
        """
        today = date.today()

        # 不能新增以前的日期
        if schedule_date < today:
            raise ValueError(f"不能新增過去的日期: {schedule_date}")

        # 不能預約超過 3 個月的日期
        max_date = today.replace(month=today.month + self.MAX_MONTHS_AHEAD)
        if schedule_date > max_date:
            raise ValueError(
                f"不能預約超過 {self.MAX_MONTHS_AHEAD} 個月的日期: {schedule_date}"
            )

    def _validate_time_range(self, start_time: time, end_time: time) -> None:
        """
        驗證時間範圍。

        Args:
            start_time: 開始時間
            end_time: 結束時間

        Raises:
            ValueError: 當時間範圍無效時
        """
        # 驗證時間格式
        self._validate_time_format(start_time, "start_time")
        self._validate_time_format(end_time, "end_time")

        # 結束時間必須晚於開始時間
        if end_time <= start_time:
            raise ValueError(f"結束時間 ({end_time}) 必須晚於開始時間 ({start_time})")

    def _validate_time_format(self, time_obj: time, field_name: str) -> None:
        """
        驗證時間格式。

        Args:
            time_obj: 要驗證的時間物件
            field_name: 欄位名稱

        Raises:
            ValueError: 當時間格式無效時
        """
        # 檢查小時範圍 (00-23)
        if not (0 <= time_obj.hour <= 23):
            raise ValueError(
                f"「{field_name}」時數「{time_obj.hour}」超過 23，請輸入00-23之間的數字"
            )

        # 檢查分鐘範圍 (00-59)
        if not (0 <= time_obj.minute <= 59):
            raise ValueError(
                f"「{field_name}」分數「{time_obj.minute}」超過 59，請輸入00-59之間的數字"
            )

    def _validate_business_hours(self, start_time: time, end_time: time) -> None:
        """
        驗證營業時間（排除休息時間）。

        Args:
            start_time: 開始時間
            end_time: 結束時間

        Raises:
            ValueError: 當時間在休息時間內時
        """
        # 檢查開始時間是否在休息時間內
        if self._is_in_rest_period(start_time):
            raise ValueError(
                f"開始時間 ({start_time}) 在休息時間內 ({self.REST_START_TIME}-{self.REST_END_TIME})"
            )

        # 檢查結束時間是否在休息時間內
        if self._is_in_rest_period(end_time):
            raise ValueError(
                f"結束時間 ({end_time}) 在休息時間內 ({self.REST_START_TIME}-{self.REST_END_TIME})"
            )

    def _is_in_rest_period(self, check_time: time) -> bool:
        """檢查時間是否在休息時間內。"""
        # 休息時間跨越午夜 (例如: 22:00-06:00 或 00:00-08:00)
        if self.REST_START_TIME <= self.REST_END_TIME:
            # 正常情況：休息時間在同一天內
            return self.REST_START_TIME <= check_time < self.REST_END_TIME
        else:
            # 跨越午夜：休息時間跨越到隔天
            # 例如：22:00-06:00 表示 22:00-23:59 和 00:00-05:59
            return check_time >= self.REST_START_TIME or check_time < self.REST_END_TIME

    def _validate_note(self, note: str | None) -> None:
        """
        驗證備註。

        Args:
            note: 要驗證的備註

        Raises:
            ValueError: 當備註無效時
        """
        if note is not None:
            if len(note) > self.MAX_NOTE_LENGTH:
                raise ValueError(f"備註不能超過 {self.MAX_NOTE_LENGTH} 個字符")

    def _validate_schedule_overlaps(
        self, schedules: List[ScheduleData], db: Any
    ) -> None:
        """
        驗證時段重疊。

        Args:
            schedules: 要驗證的時段列表
            db: 資料庫會話

        Raises:
            BusinessLogicError: 當檢測到重疊時
        """
        self.logger.debug("檢查時段重疊")

        for schedule_data in schedules:
            overlapping_schedules = self._check_schedule_overlap(
                db=db,
                giver_id=schedule_data.giver_id,
                schedule_date=schedule_data.schedule_date,
                start_time=schedule_data.start_time,
                end_time=schedule_data.end_time,
            )

            if overlapping_schedules:
                # 格式化重疊時段的錯誤訊息
                error_msg = format_schedule_overlap_error_message(
                    overlapping_schedules,
                    schedule_data.schedule_date,
                    "建立",
                )
                raise BusinessLogicError(error_msg, ErrorCode.SCHEDULE_OVERLAP)

    def _check_schedule_overlap(
        self,
        db: Any,
        giver_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
    ) -> List[Schedule]:
        """
        檢查時段重疊。

        Args:
            db: 資料庫會話
            giver_id: Giver ID
            schedule_date: 時段日期
            start_time: 開始時間
            end_time: 結束時間

        Returns:
            List[Schedule]: 重疊的時段列表
        """
        # 查詢同一天、同一 Giver 的時段
        existing_schedules = (
            db.query(Schedule)
            .filter(
                and_(
                    Schedule.giver_id == giver_id,
                    Schedule.date == schedule_date,
                    Schedule.deleted_at.is_(None),  # 排除已刪除的時段
                )
            )
            .all()
        )

        overlapping_schedules = []
        for existing_schedule in existing_schedules:
            # 檢查時間重疊
            if self._is_time_overlapping(
                start_time,
                end_time,
                existing_schedule.start_time,
                existing_schedule.end_time,
            ):
                overlapping_schedules.append(existing_schedule)

        return overlapping_schedules

    def _is_time_overlapping(
        self,
        start1: time,
        end1: time,
        start2: time,
        end2: time,
    ) -> bool:
        """
        檢查兩個時間範圍是否重疊。

        Args:
            start1: 第一個時間範圍的開始時間
            end1: 第一個時間範圍的結束時間
            start2: 第二個時間範圍的開始時間
            end2: 第二個時間範圍的結束時間

        Returns:
            bool: 是否重疊
        """
        return start1 < end2 and start2 < end1

    def validate_user_exists(self, db: Any, user_id: int, role_name: str) -> Any:
        """
        驗證使用者是否存在。

        Args:
            db: 資料庫會話
            user_id: 使用者 ID
            role_name: 角色名稱（用於錯誤訊息）

        Returns:
            User: 使用者物件

        Raises:
            NotFoundError: 當使用者不存在時
        """
        from app.models.user import User

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(f"{role_name}", user_id)
        return user

    def validate_creator_permissions(
        self, created_by: int, created_by_role: UserRoleEnum
    ) -> None:
        """
        驗證建立者權限。

        Args:
            created_by: 建立者 ID
            created_by_role: 建立者角色

        Raises:
            ValueError: 當權限不足時
        """
        # 這裡可以添加更多權限驗證邏輯
        # 例如：檢查使用者是否有建立時段的權限
        self.logger.debug(f"驗證建立者權限: {created_by} ({created_by_role.value})")
