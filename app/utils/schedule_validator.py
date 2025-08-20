"""
時段驗證器模組。

提供時段相關的驗證功能，包括日期、時間、重疊檢查等。
"""

import logging
from datetime import date, datetime, time
from typing import Any, List

from sqlalchemy import and_

from app.enums.models import UserRoleEnum
from app.errors import (
    BusinessLogicError,
    ErrorCode,
    NotFoundError,
    format_schedule_overlap_error_message,
)
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas import ScheduleData
from app.validation import TypeValidators, validate_schedule_data_complete


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

        # 使用新的驗證函數
        validate_schedule_data_complete(
            schedule_data,
            skip_date_validation=skip_date_validation,
            max_months_ahead=self.MAX_MONTHS_AHEAD,
            max_note_length=self.MAX_NOTE_LENGTH,
        )

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

        # 驗證列表參數 - 檢查是否為列表且不為空
        if not isinstance(schedules, list):
            raise ValueError("schedules 必須是列表")
        if len(schedules) == 0:
            raise ValueError("schedules 不能為空列表")

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

    def check_schedule_overlap(
        self,
        db: Any,
        giver_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: int | None = None,
    ) -> List[Schedule]:
        """
        檢查時段重疊（排除已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            giver_id: Giver ID
            schedule_date: 時段日期
            start_time: 開始時間
            end_time: 結束時間
            exclude_schedule_id: 要排除的時段 ID（用於更新時排除自己）

        Returns:
            List[Schedule]: 重疊的時段列表（排除已軟刪除的記錄）
        """
        return self.check_schedule_overlap_static(
            db, giver_id, schedule_date, start_time, end_time, exclude_schedule_id
        )

    @staticmethod
    def check_schedule_overlap_static(
        db: Any,
        giver_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: int | None = None,
    ) -> List[Schedule]:
        """
        檢查時段重疊（靜態方法，排除已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            giver_id: Giver ID
            schedule_date: 時段日期
            start_time: 開始時間
            end_time: 結束時間
            exclude_schedule_id: 要排除的時段 ID（用於更新時排除自己）

        Returns:
            List[Schedule]: 重疊的時段列表（排除已軟刪除的記錄）
        """
        # 查詢同一天同一 giver 的所有時段（排除已軟刪除的記錄）
        query = db.query(Schedule).filter(
            and_(
                Schedule.giver_id == giver_id,
                Schedule.date == schedule_date,
                Schedule.deleted_at.is_(None),
            )
        )

        # 排除指定時段（用於更新時排除自己）
        if exclude_schedule_id is not None:
            query = query.filter(Schedule.id != exclude_schedule_id)

        existing_schedules = query.all()
        overlapping_schedules = []

        for existing_schedule in existing_schedules:
            # 檢查時間重疊：新時段的開始時間 < 現有時段的結束時間 且 新時段的結束時間 > 現有時段的開始時間
            if (
                start_time < existing_schedule.end_time
                and end_time > existing_schedule.start_time
            ):
                overlapping_schedules.append(existing_schedule)

        return overlapping_schedules

    def _check_schedule_overlap(
        self,
        db: Any,
        giver_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
    ) -> List[Schedule]:
        """
        檢查時段重疊（內部方法，用於驗證）。

        Args:
            db: 資料庫會話
            giver_id: Giver ID
            schedule_date: 時段日期
            start_time: 開始時間
            end_time: 結束時間

        Returns:
            List[Schedule]: 重疊的時段列表
        """
        # 使用公開方法進行檢查
        return self.check_schedule_overlap(
            db, giver_id, schedule_date, start_time, end_time
        )

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
