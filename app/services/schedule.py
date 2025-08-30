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
    handle_service_errors_sync,
    log_operation,
)
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.enums.operations import OperationContext
from app.errors import (
    ConflictError,
)
from app.models.schedule import Schedule
from app.schemas import ScheduleBase

# 模組級別 logger
logger = logging.getLogger(__name__)


class ScheduleService:
    """時段服務類別。"""

    def __init__(self) -> None:
        """初始化服務實例。"""
        self.schedule_crud = ScheduleCRUD()

    def check_schedule_overlap(
        self,
        db: Session,
        giver_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: int | None = None,
    ) -> list[Schedule]:
        """檢查單一時段重疊。"""
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

        # 檢查時間重疊：確保新時段與現有時段不重疊
        overlapping_schedules = query.filter(
            and_(
                start_time < Schedule.end_time,
                end_time > Schedule.start_time,
                Schedule.deleted_at.is_(None),
            )
        ).all()

        logger.info(
            f"時段重疊檢查完成: giver_id={giver_id}, date={schedule_date}, "
            f"time={start_time}-{end_time}, 重疊數量={len(overlapping_schedules)}"
        )

        return overlapping_schedules

    def check_multiple_schedules_overlap(
        self,
        db: Session,
        schedules: list[ScheduleBase],
    ) -> list[Schedule]:
        """檢查多個時段的重疊情況。"""
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

        # 不做錯誤處理，由上層統一處理錯誤日誌

        return all_overlapping_schedules

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

    def log_schedule_details(
        self,
        schedules: list[ScheduleBase],
        context: OperationContext = OperationContext.CREATE,
    ) -> None:
        """記錄時段詳情。

        Args:
            schedules: 時段資料列表
            context: 操作上下文，預設為建立操作
        """
        if not schedules:
            logger.info(f"{context.value}時段: 無時段資料")
            return

        schedule_details = []
        for i, schedule_data in enumerate(schedules):
            detail = (
                f"時段{i+1}: {schedule_data.schedule_date} "
                f"{schedule_data.start_time}-{schedule_data.end_time}"
            )
            schedule_details.append(detail)
        logger.info(f"{context.value}時段詳情: {', '.join(schedule_details)}")

    def create_schedule_orm_objects(
        self,
        schedules: list[ScheduleBase],
        created_by: int,
        created_by_role: UserRoleEnum,
    ) -> list[Schedule]:
        """建立時段 ORM 物件列表。"""
        schedule_orm_objects = []
        for schedule_data in schedules:
            # 根據建立者角色決定時段狀態
            status = self.determine_schedule_status(created_by_role, schedule_data)

            schedule_orm = Schedule(
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
            schedule_orm_objects.append(schedule_orm)

        return schedule_orm_objects

    @handle_service_errors_sync("建立時段")
    @log_operation("建立時段")
    def create_schedules(
        self,
        db: Session,
        schedules: list[ScheduleBase],
        created_by: int,
        created_by_role: UserRoleEnum,
    ) -> list[Schedule]:
        """建立多個時段。"""
        self.log_schedule_details(schedules, OperationContext.CREATE)

        overlapping_schedules = self.check_multiple_schedules_overlap(db, schedules)
        if overlapping_schedules:
            error_msg = (
                f"檢測到 {len(overlapping_schedules)} 個重疊時段，請調整時段之時間"
            )
            raise ConflictError(error_msg)

        created_schedules = self.create_schedule_orm_objects(
            schedules, created_by, created_by_role
        )

        created_schedules = self.schedule_crud.create_schedules(db, created_schedules)

        logger.info(
            f"成功建立 {len(created_schedules)} 個時段，"
            f"ID 範圍: {[s.id for s in created_schedules]}"
        )

        return created_schedules

    @handle_service_errors_sync("查詢時段列表")
    @log_operation("查詢時段列表")
    def list_schedules(
        self,
        db: Session,
        giver_id: int | None = None,
        taker_id: int | None = None,
        status_filter: str | None = None,
    ) -> list[Schedule]:
        """查詢時段列表。"""
        schedules = self.schedule_crud.list_schedules(
            db, giver_id, taker_id, status_filter
        )

        logger.info(
            f"查詢時段列表完成: giver_id={giver_id}, taker_id={taker_id}, "
            f"status_filter={status_filter}, 找到 {len(schedules)} 個時段"
        )
        return schedules

    @handle_service_errors_sync("查詢單一時段")
    @log_operation("查詢單一時段")
    def get_schedule(
        self,
        db: Session,
        schedule_id: int,
    ) -> Schedule:
        """根據 ID 查詢單一時段。"""
        schedule = self.schedule_crud.get_schedule(db, schedule_id)

        logger.info(
            f"查詢時段完成: schedule_id={schedule_id}, "
            f"giver_id={schedule.giver_id}, taker_id={schedule.taker_id}, "
            f"status={schedule.status.value}, date={schedule.date}"
        )

        return schedule

    def new_updated_time_values(
        self,
        db: Session,
        schedule_id: int,
        **kwargs: Any,
    ) -> tuple[date, time, time]:
        """更新後的時間值。"""
        schedule = self.schedule_crud.get_schedule(db, schedule_id)

        new_date = kwargs.get("schedule_date", schedule.date)
        new_start_time = kwargs.get("start_time", schedule.start_time)
        new_end_time = kwargs.get("end_time", schedule.end_time)

        return new_date, new_start_time, new_end_time

    def check_update_overlap(
        self,
        db: Session,
        schedule_id: int,
        **kwargs: Any,
    ) -> list[Schedule]:
        """檢查更新時段時的重疊情況。"""
        # 如果更新了日期、開始時間或結束時間，就需要進行重疊檢查
        need_overlap_check = any(
            field in kwargs for field in ["schedule_date", "start_time", "end_time"]
        )

        if not need_overlap_check:
            return []

        schedule = self.schedule_crud.get_schedule(db, schedule_id)
        new_date, new_start_time, new_end_time = self.new_updated_time_values(
            db, schedule_id, **kwargs
        )

        # 檢查重疊（排除自己）
        overlapping_schedules = self.check_schedule_overlap(
            db=db,
            giver_id=schedule.giver_id,
            schedule_date=new_date,
            start_time=new_start_time,
            end_time=new_end_time,
            exclude_schedule_id=schedule_id,
        )

        return overlapping_schedules

    @handle_service_errors_sync("更新時段")
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
        overlapping_schedules = self.check_update_overlap(db, schedule_id, **kwargs)

        if overlapping_schedules:
            error_msg = f"更新時段 {schedule_id} 時，檢測到 {len(overlapping_schedules)} 個重疊時段，請調整時段之時間"
            raise ConflictError(error_msg)

        updated_schedule = self.schedule_crud.update_schedule(
            db=db,
            schedule_id=schedule_id,
            updated_by=updated_by,
            updated_by_role=updated_by_role,
            **kwargs,
        )

        return updated_schedule

    @handle_service_errors_sync("軟刪除時段")
    @log_operation("軟刪除時段")
    def delete_schedule(
        self,
        db: Session,
        schedule_id: int,
        deleted_by: int | None = None,
        deleted_by_role: UserRoleEnum | None = None,
    ) -> bool:
        """軟刪除時段。"""
        deletion_success = self.schedule_crud.delete_schedule(
            db, schedule_id, deleted_by, deleted_by_role
        )

        if deletion_success:
            logger.info(
                f"時段 {schedule_id} 軟刪除成功, "
                f"deleted_by={deleted_by}, role={deleted_by_role}"
            )
        else:
            logger.warning(
                f"時段 {schedule_id} 軟刪除失敗, "
                f"deleted_by={deleted_by}, role={deleted_by_role}"
            )

        return deletion_success


schedule_service = ScheduleService()
