"""時段服務層模組。

提供時段相關的業務邏輯處理，包括時段重疊檢查、時段管理等。
"""

# ===== 標準函式庫 =====
from datetime import date, time
import logging
from typing import Any

# ===== 第三方套件 =====
from sqlalchemy import and_
from sqlalchemy.orm import Session

# ===== 本地模組 =====
from app.crud.schedule import ScheduleCRUD
from app.decorators import (
    handle_service_errors,
    log_operation,
)
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.errors import (
    ConflictError,
)
from app.models.schedule import Schedule
from app.schemas import ScheduleBase


class ScheduleService:
    """時段服務類別。"""

    def __init__(self) -> None:
        """初始化服務實例。"""
        self.logger = logging.getLogger(__name__)
        self.schedule_crud = ScheduleCRUD()

    @log_operation("檢查時段重疊")
    def check_schedule_overlap(
        self,
        db: Session,
        giver_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: int | None = None,
    ) -> list[Schedule]:
        """檢查時段重疊。"""
        # 驗證時間範圍：確保輸入的時間範圍是有效的
        if end_time <= start_time:
            raise ValueError(f"結束時間 ({end_time}) 必須晚於開始時間 ({start_time})")

        # 建立查詢條件
        query = (
            db.query(Schedule)
            .options(*self.schedule_crud.get_schedule_query_options())
            .filter(
                Schedule.giver_id == giver_id,
                Schedule.date == schedule_date,
                Schedule.deleted_at.is_(None),
            )
        )

        # 排除指定的時段 ID（用於更新時排除自己）
        if exclude_schedule_id is not None:
            query = query.filter(Schedule.id != exclude_schedule_id)

        # 檢查時間重疊
        overlapping_schedules = query.filter(
            and_(start_time < Schedule.end_time, end_time > Schedule.start_time)
        ).all()

        self.logger.info(
            f"時段重疊檢查完成: giver_id={giver_id}, date={schedule_date}, "
            f"time={start_time}-{end_time}, 重疊數量={len(overlapping_schedules)}"
        )

        return overlapping_schedules

    def determine_schedule_status(
        self,
        created_by_role: UserRoleEnum,
        schedule_data: ScheduleBase,
    ) -> ScheduleStatusEnum:
        """根據建立者角色決定時段狀態。"""
        if created_by_role == UserRoleEnum.TAKER:
            return ScheduleStatusEnum.PENDING
        elif created_by_role == UserRoleEnum.GIVER:
            return ScheduleStatusEnum.AVAILABLE
        else:
            # 使用傳入的狀態或預設為 DRAFT
            return schedule_data.status or ScheduleStatusEnum.DRAFT

    def log_schedule_details(self, schedules: list[ScheduleBase]) -> None:
        """記錄時段詳情。"""
        schedule_details = []
        for i, schedule_data in enumerate(schedules):
            detail = (
                f"時段{i+1}: {schedule_data.schedule_date} "
                f"{schedule_data.start_time}-{schedule_data.end_time}"
            )
            schedule_details.append(detail)
        self.logger.info(f"建立時段詳情: {', '.join(schedule_details)}")

    @log_operation("建立時段物件列表")
    def create_schedule_objects(
        self,
        schedules: list[ScheduleBase],
        created_by: int,
        created_by_role: UserRoleEnum,
    ) -> list[Schedule]:
        """建立時段物件列表。"""
        schedule_objects = []
        for schedule_data in schedules:
            # 根據建立者角色決定時段狀態
            status = self.determine_schedule_status(created_by_role, schedule_data)

            schedule = Schedule(
                giver_id=schedule_data.giver_id,
                taker_id=schedule_data.taker_id,
                date=schedule_data.schedule_date,
                start_time=schedule_data.start_time,
                end_time=schedule_data.end_time,
                note=schedule_data.note,
                status=status,
                created_by=created_by,
                created_by_role=created_by_role,
                updated_by=created_by,
                updated_by_role=created_by_role,
                deleted_by=None,
                deleted_by_role=None,
            )
            schedule_objects.append(schedule)

        return schedule_objects

    @handle_service_errors("建立多個時段")
    @log_operation("建立多個時段")
    def create_schedules(
        self,
        db: Session,
        schedules: list[ScheduleBase],
        created_by: int,
        created_by_role: UserRoleEnum,
    ) -> list[Schedule]:
        """建立多個時段。"""
        # 記錄即將建立的時段詳情
        self.log_schedule_details(schedules)

        # 檢查時段重疊
        all_overlapping_schedules = []
        for schedule_data in schedules:
            overlapping_schedules = self.check_schedule_overlap(
                db=db,
                giver_id=schedule_data.giver_id,
                schedule_date=schedule_data.schedule_date,
                start_time=schedule_data.start_time,
                end_time=schedule_data.end_time,
            )
            if overlapping_schedules:
                all_overlapping_schedules.extend(overlapping_schedules)

        # 如果檢測到重疊，拋出錯誤
        if all_overlapping_schedules:
            error_msg = f"時段重疊：檢測到 {len(all_overlapping_schedules)} 個重疊時段"
            self.logger.warning(f"建立時段時檢測到重疊: {error_msg}")
            raise ConflictError(error_msg)

        # 建立時段物件列表
        schedule_objects = self.create_schedule_objects(
            schedules, created_by, created_by_role
        )

        # 使用 CRUD 層建立時段
        schedule_objects = self.schedule_crud.create_schedules(db, schedule_objects)

        return schedule_objects

    @handle_service_errors("查詢時段列表")
    @log_operation("查詢時段列表")
    def get_schedules(
        self,
        db: Session,
        giver_id: int | None = None,
        taker_id: int | None = None,
        status_filter: str | None = None,
    ) -> list[Schedule]:
        """查詢時段列表。"""
        # 使用 CRUD 層查詢時段
        schedules = self.schedule_crud.get_schedules(
            db, giver_id, taker_id, status_filter
        )

        self.logger.info(f"查詢完成，找到 {len(schedules)} 個時段")
        return schedules

    @handle_service_errors("查詢單一時段")
    @log_operation("查詢單一時段")
    def get_schedule_by_id(
        self,
        db: Session,
        schedule_id: int,
    ) -> Schedule:
        """根據 ID 查詢單一時段。"""
        # 使用 CRUD 層查詢時段
        schedule = self.schedule_crud.get_schedule_by_id(db, schedule_id)

        return schedule

    @handle_service_errors("更新時段")
    @log_operation("更新時段")
    def update_schedule(
        self,
        db: Session,
        schedule_id: int,
        updated_by: int,
        updated_by_role: UserRoleEnum,
        **kwargs: Any,
    ) -> Schedule:
        """更新時段。"""
        # 檢查是否需要進行重疊檢查：如果更新了日期、開始時間或結束時間，就需要檢查重疊
        need_overlap_check = any(
            field in kwargs for field in ["schedule_date", "start_time", "end_time"]
        )

        if need_overlap_check:
            # 先取得現有時段資訊
            schedule = self.schedule_crud.get_schedule_by_id(db, schedule_id)

            # 取得更新後的時間值
            new_date = kwargs.get("schedule_date", schedule.date)
            new_start_time = kwargs.get("start_time", schedule.start_time)
            new_end_time = kwargs.get("end_time", schedule.end_time)

            # 檢查重疊（排除自己）
            overlapping_schedules = self.check_schedule_overlap(
                db=db,
                giver_id=schedule.giver_id,
                schedule_date=new_date,
                start_time=new_start_time,
                end_time=new_end_time,
                exclude_schedule_id=schedule_id,
            )

            if overlapping_schedules:
                error_msg = f"時段重疊：檢測到 {len(overlapping_schedules)} 個重疊時段"
                self.logger.warning(f"更新時段 {schedule_id} 時檢測到重疊: {error_msg}")
                raise ConflictError(error_msg)

        # 使用 CRUD 層更新時段
        updated_schedule = self.schedule_crud.update_schedule(
            db, schedule_id, updated_by, updated_by_role, **kwargs
        )

        return updated_schedule

    @handle_service_errors("軟刪除時段")
    @log_operation("軟刪除時段")
    def delete_schedule(
        self,
        db: Session,
        schedule_id: int,
        deleted_by: int | None = None,
        deleted_by_role: UserRoleEnum | None = None,
    ) -> bool:
        """軟刪除時段。"""
        # 使用 CRUD 層執行軟刪除
        deletion_success = self.schedule_crud.delete_schedule(
            db, schedule_id, deleted_by, deleted_by_role
        )

        if deletion_success:
            self.logger.info(f"時段 {schedule_id} 軟刪除成功")
        else:
            self.logger.warning(f"時段 {schedule_id} 軟刪除失敗")

        return deletion_success


# 建立服務實例
schedule_service = ScheduleService()
