"""
時段服務層模組。

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
from app.crud.user import UserCRUD
from app.decorators import (
    handle_crud_errors_with_rollback,
    log_operation,
)
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.errors import (
    BusinessLogicError,
    ErrorCode,
)
from app.models.schedule import Schedule
from app.schemas import ScheduleData


class ScheduleService:
    """時段服務類別。"""

    def __init__(self):
        """初始化服務實例。"""
        self.logger = logging.getLogger(__name__)
        self.schedule_crud = ScheduleCRUD()
        self.user_crud = UserCRUD()

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
        """
        檢查時段重疊（業務邏輯層）。

        Args:
            db: 資料庫會話
            giver_id: Giver ID
            schedule_date: 時段日期
            start_time: 開始時間
            end_time: 結束時間
            exclude_schedule_id: 要排除的時段 ID（用於更新時排除自己）

        Returns:
            list[Schedule]: 重疊的時段列表

        Raises:
            BusinessLogicError: 當檢測到重疊時
            DatabaseError: 當資料庫操作失敗時
        """

        # 驗證時間範圍
        if end_time <= start_time:
            raise BusinessLogicError(
                f"結束時間 ({end_time}) 必須晚於開始時間 ({start_time})",
                ErrorCode.BUSINESS_LOGIC_ERROR,
            )

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
        # 重疊條件：新時段的開始時間 < 現有時段的結束時間 AND 新時段的結束時間 > 現有時段的開始時間
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
        schedule_data: ScheduleData,
    ) -> ScheduleStatusEnum:
        """
        根據建立者角色決定時段狀態。

        Args:
            created_by_role: 建立者角色
            schedule_data: 時段資料

        Returns:
            ScheduleStatusEnum: 時段狀態
        """
        if created_by_role == UserRoleEnum.TAKER:
            return ScheduleStatusEnum.PENDING
        elif created_by_role == UserRoleEnum.GIVER:
            return ScheduleStatusEnum.AVAILABLE
        else:
            # 使用傳入的狀態或預設為 DRAFT
            return schedule_data.status or ScheduleStatusEnum.DRAFT

    def log_schedule_details(self, schedules: list[ScheduleData]) -> None:
        """
        記錄時段詳情。

        Args:
            schedules: 時段資料列表
        """
        schedule_details = []
        for i, schedule_data in enumerate(schedules):
            detail = (
                f"時段{i+1}: {schedule_data.schedule_date} "
                f"{schedule_data.start_time}-{schedule_data.end_time}"
            )
            schedule_details.append(detail)
        self.logger.info(f"建立時段詳情: {', '.join(schedule_details)}")

    def create_schedule_objects(
        self,
        schedules: list[ScheduleData],
        created_by: int,
        created_by_role: UserRoleEnum,
    ) -> list[Schedule]:
        """
        建立時段物件列表。

        此方法只負責建立時段物件，不執行資料庫操作。
        如果需要完整的建立流程，請使用 create_schedules 方法。

        Args:
            schedules: 時段資料列表
            created_by: 建立者 ID
            created_by_role: 建立者角色

        Returns:
            list[Schedule]: 時段物件列表
        """
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

    @handle_crud_errors_with_rollback("建立時段")
    @log_operation("建立時段")
    def create_schedules(
        self,
        db: Session,
        schedules: list[ScheduleData],
        created_by: int,
        created_by_role: UserRoleEnum,
    ) -> list[Schedule]:
        """
        建立多個時段（業務邏輯層）。

        Args:
            db: 資料庫會話
            schedules: 要建立的時段列表
            created_by: 建立者的使用者 ID
            created_by_role: 建立者的角色

        Returns:
            list[Schedule]: 建立成功的時段列表

        Raises:
            BusinessLogicError: 當檢測到時段重疊時
        """
        # 記錄建立操作
        self.logger.info(
            f"使用者 {created_by} (角色: {created_by_role.value}) "
            f"正在建立 {len(schedules)} 個時段"
        )

        # 記錄即將建立的時段詳情
        self.log_schedule_details(schedules)

        # 建立時段物件列表
        schedule_objects = self.create_schedule_objects(
            schedules, created_by, created_by_role
        )

        # 使用 CRUD 層建立時段
        created_schedules = self.schedule_crud.create_schedules(db, schedule_objects)

        self.logger.info(
            f"成功建立 {len(created_schedules)} 個時段，"
            f"ID範圍: {[s.id for s in created_schedules]}"
        )

        return created_schedules

    @handle_crud_errors_with_rollback("查詢時段列表")
    @log_operation("查詢時段列表")
    def get_schedules(
        self,
        db: Session,
        giver_id: int | None = None,
        taker_id: int | None = None,
        status_filter: str | None = None,
    ) -> list[Schedule]:
        """
        查詢時段列表（業務邏輯層）。

        Args:
            db: 資料庫會話
            giver_id: 可選的 Giver ID 篩選條件
            taker_id: 可選的 Taker ID 篩選條件
            status_filter: 可選的狀態篩選條件

        Returns:
            list[Schedule]: 符合條件的時段列表

        Raises:
            DatabaseError: 當資料庫操作失敗時
            ValueError: 當輸入參數無效時
        """
        # 記錄查詢操作
        self.logger.info(
            f"查詢時段列表: giver_id={giver_id}, taker_id={taker_id}, "
            f"status_filter={status_filter}"
        )

        # 使用 CRUD 層查詢時段
        schedules = self.schedule_crud.get_schedules(
            db, giver_id, taker_id, status_filter
        )

        self.logger.info(f"查詢完成，找到 {len(schedules)} 個時段")
        return schedules

    @handle_crud_errors_with_rollback("查詢單一時段")
    @log_operation("查詢單一時段")
    def get_schedule_by_id(self, db: Session, schedule_id: int) -> Schedule:
        """
        根據 ID 查詢單一時段（業務邏輯層）。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID

        Returns:
            Schedule: 找到的時段物件

        Raises:
            NotFoundError: 當時段不存在或已軟刪除時
        """
        # 記錄查詢操作
        self.logger.info(f"查詢時段: schedule_id={schedule_id}")

        # 使用 CRUD 層查詢時段
        schedule = self.schedule_crud.get_schedule_by_id(db, schedule_id)

        self.logger.info(f"時段 {schedule_id} 查詢成功")
        return schedule

    @handle_crud_errors_with_rollback("查詢單一時段（包含已刪除）")
    @log_operation("查詢單一時段（包含已刪除）")
    def get_schedule_by_id_including_deleted(
        self, db: Session, schedule_id: int
    ) -> Schedule | None:
        """
        根據 ID 查詢單一時段（包含已軟刪除的記錄）（業務邏輯層）。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID

        Returns:
            Schedule | None: 找到的時段物件，如果不存在則返回 None

        Raises:
            DatabaseError: 當資料庫操作失敗時
        """
        # 記錄查詢操作
        self.logger.info(f"查詢時段（包含已刪除）: schedule_id={schedule_id}")

        # 使用 CRUD 層查詢時段
        schedule = self.schedule_crud.get_schedule_by_id_including_deleted(
            db, schedule_id
        )

        if schedule:
            self.logger.info(f"時段 {schedule_id} 查詢成功（包含已刪除記錄）")
        else:
            self.logger.info(f"時段 {schedule_id} 不存在")

        return schedule

    @handle_crud_errors_with_rollback("更新時段")
    @log_operation("更新時段")
    def update_schedule(
        self,
        db: Session,
        schedule_id: int,
        updated_by: int,
        updated_by_role: UserRoleEnum,
        **kwargs: Any,
    ) -> Schedule:
        """
        更新時段（業務邏輯層）。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID
            updated_by: 更新者的使用者 ID
            updated_by_role: 更新者的角色
            **kwargs: 要更新的欄位

        Returns:
            Schedule: 更新後的時段物件

        Raises:
            BusinessLogicError: 當檢測到時段重疊時
        """
        # 記錄更新操作
        self.logger.info(
            f"時段 {schedule_id} 正在被使用者 {updated_by} "
            f"(角色: {updated_by_role.value}) 更新"
        )

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
                raise BusinessLogicError(error_msg, ErrorCode.SCHEDULE_OVERLAP)

        # 使用 CRUD 層更新時段
        updated_schedule = self.schedule_crud.update_schedule(
            db, schedule_id, updated_by, updated_by_role, **kwargs
        )

        self.logger.info(f"時段 {schedule_id} 更新成功")
        return updated_schedule

    @handle_crud_errors_with_rollback("軟刪除時段")
    @log_operation("軟刪除時段")
    def delete_schedule(
        self,
        db: Session,
        schedule_id: int,
        deleted_by: int | None = None,
        deleted_by_role: UserRoleEnum | None = None,
    ) -> bool:
        """
        軟刪除時段（業務邏輯層）。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID
            deleted_by: 刪除者的使用者 ID
            deleted_by_role: 刪除者的角色

        Returns:
            bool: 刪除成功返回 True，否則返回 False

        Raises:
            DatabaseError: 當資料庫操作失敗時
        """
        # 記錄刪除操作
        if deleted_by and deleted_by_role:
            self.logger.info(
                f"時段 {schedule_id} 正在被使用者 {deleted_by} "
                f"(角色: {deleted_by_role.value}) 軟刪除"
            )

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
