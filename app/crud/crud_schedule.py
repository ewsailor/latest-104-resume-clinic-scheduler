"""
時段 CRUD 操作模組。

提供時段相關的資料庫操作，包括建立、查詢、更新和刪除時段。
"""

import logging  # 日誌記錄
from datetime import date, time  # 日期和時間處理

# ===== 標準函式庫 =====
from typing import Any, List, Optional  # 型別提示

from sqlalchemy import and_  # SQL 條件組合

# ===== 第三方套件 =====
from sqlalchemy.orm import Session  # 資料庫會話

from app.models.enums import UserRoleEnum  # ENUM 定義

# ===== 本地模組 =====
from app.models.schedule import Schedule  # 時段模型
from app.models.user import User  # 使用者模型
from app.schemas import ScheduleCreate, UserCreate  # 資料模型


class ScheduleCRUD:
    """時段 CRUD 操作類別。"""

    def __init__(self):
        """初始化 CRUD 實例，設定日誌器。"""
        self.logger = logging.getLogger(__name__)

    def create_user(self, db: Session, user: UserCreate) -> User:
        """
        建立使用者。

        Args:
            db: 資料庫會話
            user: 使用者資料

        Returns:
            User: 建立的使用者物件

        Raises:
            ValueError: 當 email 已存在時
        """
        self.logger.info(f"正在建立使用者: {user.name} ({user.email})")

        # 檢查 email 是否已存在
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            error_msg = f"電子信箱已被使用: {user.email}"
            self.logger.warning(error_msg)
            raise ValueError("此電子信箱已被使用")

        try:
            # 建立新使用者
            new_user = User(name=user.name, email=user.email)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            self.logger.info(f"成功建立使用者: ID={new_user.id}, 名稱={new_user.name}")
            return new_user
        except Exception as e:
            db.rollback()
            error_msg = f"建立使用者失敗: {str(e)}"
            self.logger.error(error_msg)
            raise

    def check_schedule_overlap(
        self,
        db: Session,
        giver_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: Optional[int] = None,
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

    def create_schedules(
        self,
        db: Session,
        schedules: List[ScheduleCreate],
        operator_user_id: int,
        operator_role: UserRoleEnum,
    ) -> List[Schedule]:
        """
        建立多個時段。

        Args:
            db: 資料庫會話
            schedules: 要建立的時段列表
            operator_user_id: 操作者的使用者 ID（建立者）
            operator_role: 操作者的角色 (UserRoleEnum)

        Returns:
            List[Schedule]: 建立成功的時段列表

        Raises:
            ValueError: 當檢測到時段重疊時或操作者不存在時
        """
        # 驗證操作者是否存在
        operator = db.query(User).filter(User.id == operator_user_id).first()
        if not operator:
            error_msg = f"操作者不存在: user_id={operator_user_id}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # 記錄建立操作
        self.logger.info(
            f"使用者 {operator_user_id} (角色: {operator_role.value}) "
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
                overlapping_info = []
                for overlap_schedule in overlapping_schedules:
                    # 格式化日期為 YYYY/MM/DD（週X）格式
                    weekday_names = [
                        '週一',
                        '週二',
                        '週三',
                        '週四',
                        '週五',
                        '週六',
                        '週日',
                    ]
                    weekday = weekday_names[overlap_schedule.date.weekday()]
                    formatted_date = (
                        f"{overlap_schedule.date.strftime('%Y/%m/%d')}（{weekday}）"
                    )

                    # 格式化時間
                    start_time_str = overlap_schedule.start_time.strftime('%H:%M')
                    end_time_str = overlap_schedule.end_time.strftime('%H:%M')

                    overlapping_info.append(
                        f"{formatted_date} {start_time_str}~{end_time_str}"
                    )

                raise ValueError(
                    f"您正輸入的時段，和您之前曾輸入的「{', '.join(overlapping_info)}」時段重複或重疊，請重新輸入"
                )

        # 建立時段物件列表
        schedule_objects = []
        for schedule_data in schedules:
            # 根據操作者角色決定時段狀態
            # GIVER 建立時段 -> AVAILABLE (可預約)
            # TAKER 建立時段 -> PENDING (等待 Giver 確認)
            if operator_role == UserRoleEnum.TAKER:
                status = "PENDING"
            elif operator_role == UserRoleEnum.GIVER:
                status = "AVAILABLE"
            else:
                # 使用傳入的狀態或預設為 DRAFT
                status = schedule_data.status or "DRAFT"

            schedule = Schedule(
                giver_id=schedule_data.giver_id,
                taker_id=schedule_data.taker_id,
                date=schedule_data.schedule_date,
                start_time=schedule_data.start_time,
                end_time=schedule_data.end_time,
                note=schedule_data.note,
                status=status,  # 使用計算的狀態
                updated_by=operator_user_id,
                updated_by_role=operator_role,
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

        try:
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

        except Exception as e:
            db.rollback()
            error_msg = f"建立時段失敗: {str(e)}"
            self.logger.error(error_msg)
            raise

    def get_schedules(
        self,
        db: Session,
        giver_id: Optional[int] = None,
        taker_id: Optional[int] = None,
        status_filter: Optional[str] = None,
    ) -> List[Schedule]:
        """
        查詢時段列表（排除已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            giver_id: 可選的 Giver ID 篩選條件
            taker_id: 可選的 Taker ID 篩選條件
            status_filter: 可選的狀態篩選條件

        Returns:
            List[Schedule]: 符合條件的時段列表（排除已軟刪除的記錄）
        """
        query = db.query(Schedule)

        # 排除已軟刪除的記錄
        query = query.filter(Schedule.deleted_at.is_(None))

        # 套用篩選條件
        filters = []
        if giver_id is not None:
            filters.append(Schedule.giver_id == giver_id)
        if taker_id is not None:
            filters.append(Schedule.taker_id == taker_id)
        if status_filter is not None:
            filters.append(Schedule.status == status_filter)

        if filters:
            query = query.filter(and_(*filters))

        return query.all()

    def get_schedule_by_id(self, db: Session, schedule_id: int) -> Optional[Schedule]:
        """
        根據 ID 查詢單一時段（排除已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID

        Returns:
            Optional[Schedule]: 找到的時段物件，如果不存在或已軟刪除則返回 None
        """
        return (
            db.query(Schedule)
            .filter(Schedule.id == schedule_id, Schedule.deleted_at.is_(None))
            .first()
        )

    def get_schedule_by_id_including_deleted(
        self, db: Session, schedule_id: int
    ) -> Optional[Schedule]:
        """
        根據 ID 查詢單一時段（包含已軟刪除的記錄）。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID

        Returns:
            Optional[Schedule]: 找到的時段物件，如果不存在則返回 None
        """
        return db.query(Schedule).filter(Schedule.id == schedule_id).first()

    def update_schedule(
        self,
        db: Session,
        schedule_id: int,
        updated_by_user_id: int,
        operator_role: UserRoleEnum,
        **kwargs: Any,
    ) -> Optional[Schedule]:
        """
        更新時段。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID
            updated_by_user_id: 操作者的使用者 ID（更新者）
            operator_role: 操作者的角色 (UserRoleEnum)
            **kwargs: 要更新的欄位

        Returns:
            Optional[Schedule]: 更新後的時段物件，如果不存在則返回 None

        Raises:
            ValueError: 當更新者不存在時
        """
        # 驗證更新者是否存在
        updater = db.query(User).filter(User.id == updated_by_user_id).first()
        if not updater:
            error_msg = f"更新者不存在: user_id={updated_by_user_id}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # 驗證時段是否存在
        schedule = self.get_schedule_by_id(db, schedule_id)
        if not schedule:
            self.logger.warning(f"嘗試更新不存在的時段: schedule_id={schedule_id}")
            return None

        # 記錄更新操作
        self.logger.info(
            f"時段 {schedule_id} 正在被使用者 {updated_by_user_id} "
            f"(角色: {operator_role.value}) 更新"
        )

        # 設定更新者資訊
        schedule.updated_by = updated_by_user_id
        schedule.updated_by_role = operator_role

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

        try:
            db.commit()
            db.refresh(schedule)
            self.logger.info(f"時段 {schedule_id} 更新成功")
            return schedule
        except Exception as e:
            db.rollback()
            error_msg = f"更新時段 {schedule_id} 失敗: {str(e)}"
            self.logger.error(error_msg)
            raise

    def delete_schedule(
        self,
        db: Session,
        schedule_id: int,
        operator_user_id: Optional[int] = None,
        operator_role: Optional[UserRoleEnum] = None,
    ) -> bool:
        """
        軟刪除時段。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID
            operator_user_id: 操作者的使用者 ID（可選，用於審計記錄）
            operator_role: 操作者的角色（可選，用於審計記錄）

        Returns:
            bool: 刪除成功返回 True，否則返回 False

        Raises:
            ValueError: 當操作者不存在時（如果提供了操作者 ID）
        """
        # 如果提供了操作者ID，驗證操作者是否存在
        if operator_user_id:
            operator = db.query(User).filter(User.id == operator_user_id).first()
            if not operator:
                error_msg = f"操作者不存在: user_id={operator_user_id}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

        self.logger.info(
            f"正在軟刪除時段 ID: {schedule_id}，操作者: {operator_user_id}"
        )

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

        # 記錄操作者資訊
        if operator_user_id and operator_role:
            self.logger.info(
                f"時段 {schedule_id} ({schedule_info}) "
                f"正在被使用者 {operator_user_id} (角色: {operator_role.value}) 軟刪除"
            )

        try:
            # 實作軟刪除：設定 deleted_at 時間戳記和更新狀態
            from app.models.enums import ScheduleStatusEnum
            from app.utils.timezone import get_local_now_naive

            schedule.deleted_at = get_local_now_naive()
            schedule.updated_at = get_local_now_naive()
            schedule.updated_by = operator_user_id
            schedule.updated_by_role = operator_role

            # 將狀態改為 CANCELLED（已取消）
            schedule.status = ScheduleStatusEnum.CANCELLED

            db.commit()
            self.logger.info(
                f"時段 {schedule_id} ({schedule_info}) 已成功軟刪除，狀態改為 CANCELLED，刪除時間: {schedule.deleted_at}"
            )
            return True
        except Exception as e:
            db.rollback()
            error_msg = f"軟刪除時段 {schedule_id} 失敗: {str(e)}"
            self.logger.error(error_msg)
            raise


# 建立 CRUD 實例
schedule_crud = ScheduleCRUD()
