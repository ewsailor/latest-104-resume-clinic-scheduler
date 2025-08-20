"""
時段 CRUD 操作模組。

提供時段相關的資料庫操作，包括建立、查詢、更新和刪除時段。
"""

import logging  # 日誌記錄
from datetime import date, time  # 日期和時間處理

# ===== 標準函式庫 =====
from typing import Any  # 型別提示

from sqlalchemy import and_  # SQL 條件組合

# ===== 第三方套件 =====
from sqlalchemy.orm import Session, joinedload  # 資料庫會話

from app.enums.models import ScheduleStatusEnum, UserRoleEnum  # ENUM 定義

# ===== 本地模組 =====
from app.enums.operations import OperationContext  # 操作相關的 ENUM
from app.models.schedule import Schedule  # 時段模型
from app.models.user import User  # 使用者模型
from app.schemas import ScheduleData  # 資料模型
from app.utils.crud_decorators import (
    handle_crud_errors,
    handle_crud_errors_with_rollback,
    log_crud_operation,
)
from app.utils.error_handler import (
    BusinessLogicError,
    DatabaseError,
    ErrorCode,
    NotFoundError,
    create_schedule_not_found_error,
    create_schedule_overlap_error,
    create_user_not_found_error,
    format_schedule_overlap_error_message,
    handle_database_error,
    safe_execute,
)
from app.utils.timezone import get_local_now_naive  # 時區工具
from app.utils.validators import ParameterValidator, validate_parameters  # 參數驗證工具


class ScheduleCRUD:
    """時段 CRUD 操作類別。"""

    def __init__(self):
        """初始化 CRUD 實例，設定日誌器。"""
        self.logger = logging.getLogger(__name__)

    @handle_crud_errors("建立查詢選項")
    def _get_schedule_query_options(self, include_relations: list[str] | None = None):
        """
        取得時段查詢的選項設定。

        Args:
            include_relations: 要載入的關聯列表，如果為 None 則載入所有關聯

        Returns:
            list: joinedload 選項列表

        Raises:
            ValueError: 當輸入參數無效時
            Exception: 當 SQLAlchemy 操作失敗時
        """
        # 如果沒有傳入參數，使用預設值（簡化驗證）
        if include_relations is None:
            # 預設載入所有關聯
            include_relations = [
                'giver',
                'taker',
                'created_by_user',
                'updated_by_user',
                'deleted_by_user',
            ]
        else:
            # 只有在實際傳入參數時才進行驗證
            include_relations = ParameterValidator.validate_list(
                include_relations, "include_relations", str
            )

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

        self.logger.debug(f"建立查詢選項: {len(options)} 個關聯載入選項")
        return options

    @handle_crud_errors("驗證使用者存在")
    def _validate_user_exists(
        self, db: Session, user_id: int, context: str = "操作者"
    ) -> User:
        """
        驗證使用者是否存在。

        Args:
            db: 資料庫會話
            user_id: 使用者 ID
            context: 上下文描述（用於錯誤訊息）

        Returns:
            User: 使用者物件

        Raises:
            ValueError: 當輸入參數無效時
            NotFoundError: 當使用者不存在時
            DatabaseError: 當資料庫操作失敗時
        """
        user_id = ParameterValidator.validate_positive_int(user_id, "user_id")
        context = ParameterValidator.validate_string(context, "context")

        # 執行資料庫查詢
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            error_msg = f"{context}不存在: user_id={user_id}"
            self.logger.error(error_msg)
            raise create_user_not_found_error(user_id)

        self.logger.debug(f"驗證使用者存在成功: user_id={user_id}, context={context}")
        return user

    @handle_crud_errors("檢查時段重疊")
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
        檢查時段重疊（排除已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            giver_id: Giver ID
            schedule_date: 時段日期
            start_time: 開始時間
            end_time: 結束時間
            exclude_schedule_id: 要排除的時段 ID（用於更新時排除自己）

        Returns:
            list[Schedule]: 重疊的時段列表（排除已軟刪除的記錄）

        Raises:
            DatabaseError: 當資料庫操作失敗時
            ValueError: 當輸入參數無效時
        """
        # 使用新的驗證工具
        giver_id = ParameterValidator.validate_positive_int(giver_id, "giver_id")
        schedule_date = ParameterValidator.validate_date(schedule_date, "schedule_date")
        start_time = ParameterValidator.validate_time(start_time, "start_time")
        end_time = ParameterValidator.validate_time(end_time, "end_time")
        exclude_schedule_id = ParameterValidator.validate_optional_positive_int(
            exclude_schedule_id, "exclude_schedule_id"
        )

        # 驗證時間範圍
        ParameterValidator.validate_time_range(start_time, end_time)

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

        self.logger.debug(
            f"時段重疊檢查完成: giver_id={giver_id}, date={schedule_date}, "
            f"time={start_time}-{end_time}, 找到 {len(overlapping_schedules)} 個重疊時段"
        )

        return overlapping_schedules

    @handle_crud_errors_with_rollback("建立時段")
    @log_crud_operation("建立時段", log_args=False)
    def create_schedules(
        self,
        db: Session,
        schedules: list[ScheduleData],
        created_by: int,
        created_by_role: UserRoleEnum,
    ) -> list[Schedule]:
        # 使用驗證器驗證基本參數
        ParameterValidator.validate_list(schedules, "schedules", ScheduleData)
        created_by = ParameterValidator.validate_positive_int(created_by, "created_by")
        ParameterValidator.validate_required(
            created_by_role, "created_by_role", UserRoleEnum
        )
        """
        建立多個時段。

        Args:
            db: 資料庫會話
            schedules: 要建立的時段列表
            created_by: 建立者的使用者 ID
            created_by_role: 建立者的角色 (UserRoleEnum)

        Returns:
            list[Schedule]: 建立成功的時段列表

        Raises:
            ValueError: 當檢測到時段重疊時或建立者不存在時
        """
        # 驗證建立者是否存在
        creator = self._validate_user_exists(db, created_by, "建立者")

        # 記錄建立操作
        self.logger.info(
            f"使用者 {created_by} (角色: {created_by_role.value}) "
            f"正在建立 {len(schedules)} 個時段"
        )

        # 檢查重疊時段
        for schedule_data in schedules:
            overlapping_schedules = self.check_schedule_overlap(
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
                    OperationContext.CREATE,
                )
                raise BusinessLogicError(error_msg, ErrorCode.SCHEDULE_OVERLAP)

        # 建立時段物件列表
        schedule_objects = []
        for schedule_data in schedules:
            # 根據建立者角色決定時段狀態
            # GIVER 建立時段 -> AVAILABLE (可預約)
            # TAKER 建立時段 -> PENDING (等待 Giver 確認)
            if created_by_role == UserRoleEnum.TAKER:
                status = ScheduleStatusEnum.PENDING
            elif created_by_role == UserRoleEnum.GIVER:
                status = ScheduleStatusEnum.AVAILABLE
            else:
                # 使用傳入的狀態或預設為 DRAFT
                status = schedule_data.status or ScheduleStatusEnum.DRAFT

            schedule = Schedule(
                giver_id=schedule_data.giver_id,
                taker_id=schedule_data.taker_id,
                date=schedule_data.schedule_date,
                start_time=schedule_data.start_time,
                end_time=schedule_data.end_time,
                note=schedule_data.note,
                status=status,  # 使用計算的狀態
                created_by=created_by,
                created_by_role=created_by_role,
                updated_by=created_by,
                updated_by_role=created_by_role,
                deleted_by=None,
                deleted_by_role=None,
            )
            schedule_objects.append(schedule)

        # 記錄即將建立的時段詳情
        schedule_details = []
        for i, schedule_data in enumerate(schedules):
            detail = (
                f"時段{i+1}: {schedule_data.schedule_date} "
                f"{schedule_data.start_time}-{schedule_data.end_time}"
            )
            schedule_details.append(detail)
        self.logger.info(f"建立時段詳情: {', '.join(schedule_details)}")

        # 批量新增到資料庫
        db.add_all(schedule_objects)
        db.commit()

        # 重新整理物件以取得 ID
        for schedule in schedule_objects:
            db.refresh(schedule)

        self.logger.info(
            f"成功建立 {len(schedule_objects)} 個時段，"
            f"ID範圍: {[s.id for s in schedule_objects]}"
        )
        return schedule_objects

    @handle_crud_errors("查詢時段列表")
    def get_schedules(
        self,
        db: Session,
        giver_id: int | None = None,
        taker_id: int | None = None,
        status_filter: str | None = None,
    ) -> list[Schedule]:
        """
        查詢時段列表（排除已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            giver_id: 可選的 Giver ID 篩選條件
            taker_id: 可選的 Taker ID 篩選條件
            status_filter: 可選的狀態篩選條件

        Returns:
            list[Schedule]: 符合條件的時段列表（排除已軟刪除的記錄）

        Raises:
            DatabaseError: 當資料庫操作失敗時
            ValueError: 當輸入參數無效時
        """
        # 驗證輸入參數
        giver_id = ParameterValidator.validate_optional_positive_int(
            giver_id, "giver_id"
        )
        taker_id = ParameterValidator.validate_optional_positive_int(
            taker_id, "taker_id"
        )
        status_filter = ParameterValidator.validate_optional_string(
            status_filter, "status_filter"
        )

        query = db.query(Schedule).options(*self._get_schedule_query_options())

        # 排除已軟刪除的記錄
        query = query.filter(Schedule.deleted_at.is_(None))

        # 套用篩選條件
        filters = []
        if giver_id is not None:
            filters.append(Schedule.giver_id == giver_id)
        if taker_id is not None:
            filters.append(Schedule.taker_id == taker_id)
        if status_filter is not None:
            # 使用新的驗證工具驗證枚舉值
            ParameterValidator.validate_enum_value(
                status_filter, "status_filter", ScheduleStatusEnum
            )
            status_enum = ScheduleStatusEnum(status_filter)
            filters.append(Schedule.status == status_enum)

        if filters:
            query = query.filter(and_(*filters))

        schedules = query.all()

        self.logger.debug(
            f"查詢時段列表完成: giver_id={giver_id}, taker_id={taker_id}, "
            f"status_filter={status_filter}, 找到 {len(schedules)} 個時段"
        )

        return schedules

    @validate_parameters(schedule_id=dict(type=int, min_value=1))
    def get_schedule_by_id(self, db: Session, schedule_id: int) -> Schedule:
        """
        根據 ID 查詢單一時段（排除已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID

        Returns:
            Schedule: 找到的時段物件

        Raises:
            NotFoundError: 當時段不存在或已軟刪除時
        """

        schedule = (
            db.query(Schedule)
            .options(*self._get_schedule_query_options())
            .filter(Schedule.id == schedule_id, Schedule.deleted_at.is_(None))
            .first()
        )

        if not schedule:
            raise create_schedule_not_found_error(schedule_id)

        return schedule

    @validate_parameters(schedule_id=dict(type=int, min_value=1))
    def get_schedule_by_id_including_deleted(
        self, db: Session, schedule_id: int
    ) -> Schedule | None:
        """
        根據 ID 查詢單一時段（包含已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID

        Returns:
            Schedule | None: 找到的時段物件，如果不存在則返回 None
        """

        return (
            db.query(Schedule)
            .options(*self._get_schedule_query_options())
            .filter(Schedule.id == schedule_id)
            .first()
        )

    @handle_crud_errors_with_rollback("更新時段")
    def update_schedule(
        self,
        db: Session,
        schedule_id: int,
        updated_by: int,
        updated_by_role: UserRoleEnum,
        **kwargs: Any,
    ) -> Schedule:
        # 使用驗證器驗證基本參數
        schedule_id = ParameterValidator.validate_positive_int(
            schedule_id, "schedule_id"
        )
        updated_by = ParameterValidator.validate_positive_int(updated_by, "updated_by")
        ParameterValidator.validate_required(
            updated_by_role, "updated_by_role", UserRoleEnum
        )
        """
        更新時段。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID
            updated_by: 操作者的使用者 ID（更新者）
            updated_by_role: 操作者的角色 (UserRoleEnum)
            **kwargs: 要更新的欄位

        Returns:
            Schedule: 更新後的時段物件

        Raises:
            ValueError: 當更新者不存在時
            NotFoundError: 當時段不存在時
        """
        # 驗證更新者是否存在
        updater = self._validate_user_exists(db, updated_by, "更新者")

        # 驗證時段是否存在
        schedule = self.get_schedule_by_id(db, schedule_id)
        if not schedule:
            self.logger.warning(f"嘗試更新不存在的時段: schedule_id={schedule_id}")
            raise create_schedule_not_found_error(schedule_id)

        # 記錄更新操作
        self.logger.info(
            f"時段 {schedule_id} 正在被使用者 {updated_by} "
            f"(角色: {updated_by_role.value}) 更新"
        )

        # 檢查是否需要進行重疊檢查（當更新時間相關欄位時）
        need_overlap_check = any(
            field in kwargs for field in ["schedule_date", "start_time", "end_time"]
        )

        # 如果更新了時間相關欄位，先進行重疊檢查
        if need_overlap_check:
            # 驗證時間相關欄位
            if "schedule_date" in kwargs:
                kwargs["schedule_date"] = ParameterValidator.validate_date(
                    kwargs["schedule_date"], "schedule_date"
                )
            if "start_time" in kwargs:
                kwargs["start_time"] = ParameterValidator.validate_time(
                    kwargs["start_time"], "start_time"
                )
            if "end_time" in kwargs:
                kwargs["end_time"] = ParameterValidator.validate_time(
                    kwargs["end_time"], "end_time"
                )

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
                exclude_schedule_id=schedule_id,  # 排除自己
            )

            if overlapping_schedules:
                # 格式化重疊時段的錯誤訊息
                error_msg = format_schedule_overlap_error_message(
                    overlapping_schedules, new_date, OperationContext.UPDATE
                )
                self.logger.warning(f"更新時段 {schedule_id} 時檢測到重疊: {error_msg}")
                raise BusinessLogicError(error_msg, ErrorCode.SCHEDULE_OVERLAP)

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

        db.commit()
        db.refresh(schedule)
        self.logger.info(f"時段 {schedule_id} 更新成功")
        return schedule

    @handle_crud_errors_with_rollback("軟刪除時段")
    def delete_schedule(
        self,
        db: Session,
        schedule_id: int,
        deleted_by: int | None = None,
        deleted_by_role: UserRoleEnum | None = None,
    ) -> bool:
        # 使用驗證器驗證基本參數
        schedule_id = ParameterValidator.validate_positive_int(
            schedule_id, "schedule_id"
        )
        deleted_by = ParameterValidator.validate_optional_positive_int(
            deleted_by, "deleted_by"
        )
        if deleted_by_role is not None:
            ParameterValidator.validate_required(
                deleted_by_role, "deleted_by_role", UserRoleEnum
            )
        """
        軟刪除時段。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID
            deleted_by: 刪除者的使用者 ID（可選，用於審計記錄）
            deleted_by_role: 刪除者的角色（可選，用於審計記錄）

        Returns:
            bool: 刪除成功返回 True，否則返回 False

        Raises:
            ValueError: 當刪除者不存在時（如果提供了刪除者 ID）
        """
        # 如果提供了刪除者ID，驗證刪除者是否存在
        if deleted_by:
            deleter = self._validate_user_exists(db, deleted_by, "刪除者")

        self.logger.info(f"正在軟刪除時段 ID: {schedule_id}，刪除者: {deleted_by}")

        # 查詢時段（包含已刪除的記錄，因為需要檢查是否已經被刪除）
        schedule = self.get_schedule_by_id_including_deleted(db, schedule_id)
        if not schedule:
            self.logger.warning(f"嘗試刪除不存在的時段: schedule_id={schedule_id}")
            return False

        # 檢查是否已經被軟刪除
        if schedule.deleted_at is not None:
            self.logger.warning(
                f"時段 {schedule_id} 已經被軟刪除，刪除時間: {schedule.deleted_at}"
            )
            return True

        # 記錄時段詳情
        schedule_info = (
            f"{schedule.date} {schedule.start_time}-{schedule.end_time} "
            f"(Giver ID: {schedule.giver_id})"
        )

        # 記錄刪除者資訊
        if deleted_by and deleted_by_role:
            self.logger.info(
                f"時段 {schedule_id} ({schedule_info}) "
                f"正在被使用者 {deleted_by} (角色: {deleted_by_role.value}) 軟刪除"
            )

        # 實作軟刪除：設定 deleted_at 時間戳記和更新狀態
        schedule.updated_at = get_local_now_naive()
        schedule.updated_by = deleted_by
        schedule.updated_by_role = deleted_by_role
        schedule.deleted_at = get_local_now_naive()
        schedule.deleted_by = deleted_by
        schedule.deleted_by_role = deleted_by_role

        # 將狀態改為 CANCELLED（已取消）
        schedule.status = ScheduleStatusEnum.CANCELLED

        db.commit()
        self.logger.info(
            f"時段 {schedule_id} ({schedule_info}) 已成功軟刪除，狀態改為 CANCELLED，刪除時間: {schedule.deleted_at}"
        )
        return True


# 建立 CRUD 實例
schedule_crud = ScheduleCRUD()
