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
from app.errors import (
    create_schedule_not_found_error,
)
from app.models.schedule import Schedule
from app.utils.timezone import get_local_now_naive


class ScheduleCRUD:
    """時段 CRUD 操作類別。"""

    def __init__(self) -> None:
        """初始化 CRUD 實例，設定日誌器。"""
        self.logger = logging.getLogger(__name__)

    def get_schedule_query_options(
        self, include_relations: list[str] | None = None
    ) -> list[Any]:
        """取得時段查詢的選項設定，用於優化查詢效能。

        避免存取關聯物件時，產生 N+1 查詢問題。
        """
        # 如果沒有傳入參數，使用預設值 None，預設載入所有關聯
        if include_relations is None:
            include_relations = [
                'giver',
                'taker',
                'created_by_user',
                'updated_by_user',
                'deleted_by_user',
            ]
        else:
            # 驗證輸入參數
            if not isinstance(include_relations, list):
                raise ValueError("include_relations 必須是列表")
            for relation in include_relations:
                if not isinstance(relation, str):
                    raise ValueError("include_relations 中的每個元素必須是字串")

        # 建立選項列表
        options = []
        relation_mapping = {
            'giver': joinedload(Schedule.giver),
            'taker': joinedload(Schedule.taker),
            'created_by_user': joinedload(Schedule.created_by_user),
            'updated_by_user': joinedload(Schedule.updated_by_user),
            'deleted_by_user': joinedload(Schedule.deleted_by_user),
        }

        # 驗證關聯名稱並建立選項
        invalid_relations = []
        for relation in include_relations:
            if relation in relation_mapping:
                options.append(relation_mapping[relation])
            else:
                invalid_relations.append(relation)

        # 如果有無效的關聯名稱，記錄警告
        if invalid_relations:
            self.logger.warning(f"忽略無效的關聯名稱: {invalid_relations}")

        # 記錄建立的查詢選項
        self.logger.debug(f"建立查詢選項: {len(options)} 個關聯載入選項")
        return options

    def create_schedules(
        self,
        db: Session,
        schedule_objects: list[Schedule],
    ) -> list[Schedule]:
        """建立多個時段。"""
        # 批量新增到資料庫
        db.add_all(schedule_objects)
        db.commit()

        # 重新整理物件以取得 ID
        for schedule in schedule_objects:
            db.refresh(schedule)

        # 記錄建立的時段
        self.logger.info(
            f"成功建立 {len(schedule_objects)} 個時段，"
            f"ID範圍: {[s.id for s in schedule_objects]}"
        )

        # 返回建立的時段列表
        return schedule_objects

    def get_schedules(
        self,
        db: Session,
        giver_id: int | None = None,
        taker_id: int | None = None,
        status_filter: str | None = None,
    ) -> list[Schedule]:
        """查詢時段列表，排除已軟刪除的記錄。"""
        # 建立查詢
        query = db.query(Schedule).options(*self.get_schedule_query_options())

        # 排除已軟刪除的記錄
        query = query.filter(Schedule.deleted_at.is_(None))

        # 套用篩選條件
        filters = []
        if giver_id is not None:
            filters.append(Schedule.giver_id == giver_id)
        if taker_id is not None:
            filters.append(Schedule.taker_id == taker_id)
        if status_filter is not None:
            status_enum = ScheduleStatusEnum(status_filter)
            filters.append(Schedule.status == status_enum)

        # 如果 filters 列表不為空時，使用 and_ 組合所有篩選條件
        if filters:
            query = query.filter(and_(*filters))

        # 執行查詢
        schedules = query.all()

        # 記錄查詢結果
        self.logger.info(
            f"查詢時段列表完成: giver_id={giver_id}, taker_id={taker_id}, "
            f"status_filter={status_filter}, 找到 {len(schedules)} 個時段"
        )

        # 返回時段列表
        return schedules

    def get_schedule_by_id(
        self,
        db: Session,
        schedule_id: int,
    ) -> Schedule:
        """根據 ID 查詢單一時段，排除已軟刪除的記錄。"""
        # 建立查詢
        schedule = (
            db.query(Schedule)
            .options(*self.get_schedule_query_options())
            .filter(Schedule.id == schedule_id, Schedule.deleted_at.is_(None))
            .first()
        )

        # 如果找不到時段，拋出錯誤
        if not schedule:
            raise create_schedule_not_found_error(schedule_id)

        # 返回時段
        return schedule

    def get_schedule_by_id_including_deleted(
        self,
        db: Session,
        schedule_id: int,
    ) -> Schedule | None:
        """根據 ID 查詢單一時段，包含已軟刪除的記錄。"""
        # 注意：這裡不拋出異常，因為包含已刪除的記錄可能為 None

        # 建立查詢
        schedule = (
            db.query(Schedule)
            .options(*self.get_schedule_query_options())
            .filter(Schedule.id == schedule_id)
            .first()
        )

        # 返回時段
        return schedule

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
        schedule = self.get_schedule_by_id(db, schedule_id)

        # 設定更新者資訊
        schedule.updated_by = updated_by
        schedule.updated_by_role = updated_by_role

        # 更新欄位
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
                self.logger.warning(f"忽略無效的欄位: {field}")

        # 記錄具體的更新欄位
        if updated_fields:
            self.logger.info(
                f"時段 {schedule_id} 更新欄位: {', '.join(updated_fields)}"
            )

        # 提交更新
        db.commit()
        db.refresh(schedule)

        # 記錄更新操作
        self.logger.info(
            f"時段 {schedule_id} 更新成功，更新者: {updated_by} (角色: {updated_by_role.value})"
        )

        # 返回更新後的時段
        return schedule

    def delete_schedule(
        self,
        db: Session,
        schedule_id: int,
        deleted_by: int | None = None,
        deleted_by_role: UserRoleEnum | None = None,
    ) -> bool:
        """軟刪除時段。"""
        # 檢查時段是否存在
        schedule = self.get_schedule_by_id_including_deleted(db, schedule_id)
        if not schedule:
            return False

        # 檢查是否已經被軟刪除
        if schedule.deleted_at is not None:
            return True

        # 執行軟刪除
        schedule.updated_at = get_local_now_naive()
        schedule.updated_by = deleted_by
        schedule.updated_by_role = deleted_by_role
        schedule.deleted_at = get_local_now_naive()
        schedule.deleted_by = deleted_by
        schedule.deleted_by_role = deleted_by_role
        schedule.status = ScheduleStatusEnum.CANCELLED

        # 提交更新
        db.commit()

        # 返回成功
        return True


# 建立 CRUD 實例
schedule_crud = ScheduleCRUD()
