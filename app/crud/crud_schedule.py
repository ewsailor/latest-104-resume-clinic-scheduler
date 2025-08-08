"""
時段 CRUD 操作模組。

提供時段相關的資料庫操作，包括建立、查詢、更新和刪除時段。
"""

# ===== 標準函式庫 =====
from typing import Any, List, Optional  # 型別提示

from sqlalchemy import and_  # SQL 條件組合

# ===== 第三方套件 =====
from sqlalchemy.orm import Session  # 資料庫會話

# ===== 本地模組 =====
from app.models.schedule import Schedule  # 時段模型
from app.models.user import User  # 使用者模型
from app.schemas import ScheduleCreate, UserCreate  # 資料模型


class ScheduleCRUD:
    """時段 CRUD 操作類別。"""

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
        # 檢查 email 是否已存在
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise ValueError("此電子信箱已被使用")

        # 建立新使用者
        new_user = User(name=user.name, email=user.email)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    def create_schedules(
        self, db: Session, schedules: List[ScheduleCreate]
    ) -> List[Schedule]:
        """
        建立多個時段。

        Args:
            db: 資料庫會話
            schedules: 要建立的時段列表

        Returns:
            List[Schedule]: 建立成功的時段列表
        """
        # 建立時段物件列表
        schedule_objects = []
        for schedule_data in schedules:
            schedule = Schedule(
                giver_id=schedule_data.giver_id,
                taker_id=schedule_data.taker_id,
                date=schedule_data.schedule_date,
                start_time=schedule_data.start_time,
                end_time=schedule_data.end_time,
                note=schedule_data.note,
                status=schedule_data.status,
                role=schedule_data.role,
            )
            schedule_objects.append(schedule)

        # 批量新增到資料庫
        db.add_all(schedule_objects)
        db.commit()

        # 重新整理物件以取得 ID
        for schedule in schedule_objects:
            db.refresh(schedule)

        return schedule_objects

    def get_schedules(
        self,
        db: Session,
        giver_id: Optional[int] = None,
        taker_id: Optional[int] = None,
        status_filter: Optional[str] = None,
    ) -> List[Schedule]:
        """
        查詢時段列表。

        Args:
            db: 資料庫會話
            giver_id: 可選的 Giver ID 篩選條件
            taker_id: 可選的 Taker ID 篩選條件
            status_filter: 可選的狀態篩選條件

        Returns:
            List[Schedule]: 符合條件的時段列表
        """
        query = db.query(Schedule)

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
        根據 ID 查詢單一時段。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID

        Returns:
            Optional[Schedule]: 找到的時段物件，如果不存在則返回 None
        """
        return db.query(Schedule).filter(Schedule.id == schedule_id).first()

    def update_schedule(
        self, db: Session, schedule_id: int, **kwargs: Any
    ) -> Optional[Schedule]:
        """
        更新時段。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID
            **kwargs: 要更新的欄位

        Returns:
            Optional[Schedule]: 更新後的時段物件，如果不存在則返回 None
        """
        schedule = self.get_schedule_by_id(db, schedule_id)
        if not schedule:
            return None

        # 更新欄位
        for field, value in kwargs.items():
            if field == "schedule_date":
                # 處理 schedule_date 別名，對應到模型的 date 欄位
                setattr(schedule, "date", value)
            elif hasattr(schedule, field):
                setattr(schedule, field, value)

        db.commit()
        db.refresh(schedule)
        return schedule

    def delete_schedule(self, db: Session, schedule_id: int) -> bool:
        """
        刪除時段。

        Args:
            db: 資料庫會話
            schedule_id: 時段 ID

        Returns:
            bool: 刪除成功返回 True，否則返回 False
        """
        schedule = self.get_schedule_by_id(db, schedule_id)
        if not schedule:
            return False

        db.delete(schedule)
        db.commit()
        return True


# 建立 CRUD 實例
schedule_crud = ScheduleCRUD()
