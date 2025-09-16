"""時段 CRUD 操作模組。

提供時段相關的資料庫操作，包括建立、查詢、更新和刪除時段。
"""

# ===== 標準函式庫 =====
import logging
from typing import Any

# ===== 第三方套件 =====
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.enums.operations import DeletionResult
from app.errors import (
    create_bad_request_error,
    create_schedule_not_found_error,
)
from app.models.schedule import Schedule
from app.utils.timezone import get_local_now_naive

# 模組級別 logger
logger = logging.getLogger(__name__)


class ScheduleCRUD:
    """時段 CRUD 操作類別。"""

    def __init__(self) -> None:
        """初始化 CRUD 實例。"""

    def create_schedules(
        self,
        db: Session,
        schedules: list[Schedule],
    ) -> list[Schedule]:
        """建立多個時段。"""
        db.add_all(schedules)
        db.commit()

        for schedule in schedules:
            db.refresh(schedule)

        return schedules

    def get_schedule_query_options(
        self, include_relations: list[str] | None = None
    ) -> list[Any]:
        """取得時段查詢的選項設定，用於優化查詢效能。

        避免存取關聯物件時，產生 N+1 查詢問題。
        """
        # 需要額外載入的關聯映射，因為審計關聯使用 lazy="select"
        relation_mapping = {
            'created_by_user': joinedload(Schedule.created_by_user),
            'updated_by_user': joinedload(Schedule.updated_by_user),
            'deleted_by_user': joinedload(Schedule.deleted_by_user),
        }

        # 使用集合處理有效關聯名稱，比用列表處理更高效
        valid_relations = set(relation_mapping.keys())

        # 如果沒有傳入參數，載入所有需要額外載入的關聯，因為預設值為 None
        if include_relations is None:
            return list(relation_mapping.values())

        options = []
        invalid_relations = []

        for relation in include_relations:
            if relation in valid_relations:
                options.append(relation_mapping[relation])
            else:
                invalid_relations.append(relation)

        if invalid_relations:
            logger.warning(f"忽略無效的關聯名稱: {invalid_relations}")

        logger.debug(f"建立查詢選項: {len(options)} 個關聯載入選項")

        return options

    def _apply_filters(
        self,
        query: Any,
        giver_id: int | None = None,
        taker_id: int | None = None,
        status_filter: str | None = None,
        include_deleted: bool = False,
    ) -> Any:
        """套用篩選條件到查詢。"""
        filters = []

        # 排除已軟刪除的記錄
        if not include_deleted:
            filters.append(Schedule.deleted_at.is_(None))

        # 套用其他篩選條件
        if giver_id is not None:
            filters.append(Schedule.giver_id == giver_id)  # type: ignore
        if taker_id is not None:
            filters.append(Schedule.taker_id == taker_id)  # type: ignore
        if status_filter is not None:
            status_enum = ScheduleStatusEnum(status_filter)
            filters.append(Schedule.status == status_enum)  # type: ignore

        # 如果 filters 列表不為空時，使用 and_ 組合所有篩選條件
        if filters:
            return query.filter(and_(*filters))

        return query

    def list_schedules(
        self,
        db: Session,
        giver_id: int | None = None,
        taker_id: int | None = None,
        status_filter: str | None = None,
    ) -> list[Schedule]:
        """查詢時段列表，排除已軟刪除的記錄。"""
        query = db.query(Schedule).options(*self.get_schedule_query_options())

        query = self._apply_filters(
            query, giver_id=giver_id, taker_id=taker_id, status_filter=status_filter
        )

        schedules = query.all()

        return schedules

    def get_schedule(
        self,
        db: Session,
        schedule_id: int,
    ) -> Schedule:
        """根據 ID 查詢單一時段，排除已軟刪除的記錄。"""
        query = db.query(Schedule).options(*self.get_schedule_query_options())

        query = self._apply_filters(query).filter(Schedule.id == schedule_id)

        schedule = query.first()

        if not schedule:
            raise create_schedule_not_found_error(schedule_id)

        return schedule

    def get_schedule_including_deleted(
        self,
        db: Session,
        schedule_id: int,
    ) -> Schedule | None:
        """根據 ID 查詢單一時段，包含已軟刪除的記錄。"""
        query = db.query(Schedule).options(*self.get_schedule_query_options())

        query = self._apply_filters(query, include_deleted=True).filter(
            Schedule.id == schedule_id
        )

        schedule = query.first()

        return schedule

    def _update_schedule_fields(self, schedule: Schedule, **kwargs: Any) -> list[str]:
        """更新時段欄位並返回更新的欄位記錄。"""
        updated_fields = []

        for field, value in kwargs.items():
            if field == "schedule_date":
                # 處理 schedule_date 別名，對應到模型的 date 欄位
                old_value = getattr(schedule, "date", None)
                setattr(schedule, "date", value)
                updated_fields.append(f"date: {old_value} -> {value}")
            elif hasattr(schedule, field):
                old_value = getattr(schedule, field, None)
                setattr(schedule, field, value)
                updated_fields.append(f"{field}: {old_value} -> {value}")
            else:
                logger.warning(f"忽略無效的欄位: {field}")

        return updated_fields

    def update_schedule(
        self,
        db: Session,
        schedule_id: int,
        updated_by: int,
        updated_by_role: UserRoleEnum,
        **kwargs: Any,
    ) -> Schedule:
        """更新時段。"""
        # 驗證時段是否存在
        schedule = self.get_schedule(db, schedule_id)

        # 驗證時間邏輯（只有在更新時間欄位時才檢查）
        if "start_time" in kwargs or "end_time" in kwargs:
            start_time = kwargs.get("start_time", schedule.start_time)
            end_time = kwargs.get("end_time", schedule.end_time)

            if start_time and end_time and start_time >= end_time:
                raise create_bad_request_error("開始時間必須早於結束時間")

        # 只有當時段存在時，才設定更新者資訊
        if updated_by is not None:
            schedule.updated_by = updated_by  # type: ignore
        if updated_by_role is not None:
            schedule.updated_by_role = updated_by_role  # type: ignore

        updated_fields = self._update_schedule_fields(schedule, **kwargs)

        if updated_fields:
            logger.info(f"時段 {schedule_id} 更新欄位: {', '.join(updated_fields)}")

        db.commit()
        db.refresh(schedule)

        logger.info(
            f"時段 {schedule_id} 更新成功，更新者: {updated_by} (角色: {updated_by_role.value})"
        )

        return schedule

    def delete_schedule(
        self,
        db: Session,
        schedule_id: int,
        deleted_by: int | None = None,
        deleted_by_role: UserRoleEnum | None = None,
    ) -> DeletionResult:
        """軟刪除時段。

        Returns:
            DeletionResult: 刪除結果
                - SUCCESS: 刪除成功
                - ALREADY_DELETED: 已經刪除
                - NOT_FOUND: 時段不存在
                - CANNOT_DELETE: 無法刪除（狀態不允許）
        """
        schedule = self.get_schedule_including_deleted(db, schedule_id)

        # 使用 match-case 語法處理不同的刪除情況
        match schedule:
            case None:
                return DeletionResult.NOT_FOUND
            case _ if schedule.deleted_at is not None:
                return DeletionResult.ALREADY_DELETED
            # 已接受或已完成的時段無法刪除
            # ACCEPTED: 雙方已確認面談時間，刪除會影響約定
            # COMPLETED: 面談已完成，屬於歷史記錄，不應刪除
            case _ if schedule.status in [
                ScheduleStatusEnum.ACCEPTED,
                ScheduleStatusEnum.COMPLETED,
            ]:
                return DeletionResult.CANNOT_DELETE
            case _:
                # 執行軟刪除
                schedule.updated_at = get_local_now_naive()
                schedule.updated_by = deleted_by
                schedule.updated_by_role = deleted_by_role
                schedule.deleted_at = get_local_now_naive()
                schedule.deleted_by = deleted_by
                schedule.deleted_by_role = deleted_by_role
                schedule.status = ScheduleStatusEnum.CANCELLED

                db.commit()
                return DeletionResult.SUCCESS


schedule_crud = ScheduleCRUD()
