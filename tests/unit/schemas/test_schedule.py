"""
時段相關 Pydantic 模型測試。

測試時段管理相關的請求和回應模型。
"""

# ===== 標準函式庫 =====
from datetime import date, datetime, time

# ===== 第三方套件 =====
from pydantic import ValidationError
import pytest

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum, UserRoleEnum
from app.schemas.schedule import (
    ScheduleBase,
    ScheduleCreateRequest,
    ScheduleDeleteRequest,
    SchedulePartialUpdateRequest,
    ScheduleResponse,
    ScheduleUpdateBase,
)


# ===== 測試設定 =====
class TestScheduleBase:
    """ScheduleBase 模型測試類別。"""

    def test_schedule_base_creation_success(self):
        """測試 ScheduleBase 建立成功情況。"""
        schedule = ScheduleBase(
            giver_id=1,
            taker_id=2,
            status=ScheduleStatusEnum.AVAILABLE,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
        )

        assert schedule.giver_id == 1
        assert schedule.taker_id == 2
        assert schedule.status == ScheduleStatusEnum.AVAILABLE
        assert schedule.schedule_date == date(2024, 1, 15)
        assert schedule.start_time == time(9, 0)
        assert schedule.end_time == time(10, 0)
        assert schedule.note == "測試時段"

    def test_schedule_base_creation_with_minimal_data(self):
        """測試 ScheduleBase 使用最少資料建立。"""
        schedule = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        assert schedule.giver_id == 1
        assert schedule.taker_id is None
        assert schedule.status is None  # 預設值為 None
        assert schedule.schedule_date == date(2024, 1, 15)
        assert schedule.start_time == time(9, 0)
        assert schedule.end_time == time(10, 0)
        assert schedule.note is None

    def test_schedule_base_validation_giver_id_required(self):
        """測試 ScheduleBase giver_id 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                end_time=time(10, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "giver_id" in str(error["loc"])
            for error in errors
        )

    def test_schedule_base_validation_giver_id_positive(self):
        """測試 ScheduleBase giver_id 必須為正數。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(
                giver_id=0,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                end_time=time(10, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "greater_than" and "giver_id" in str(error["loc"])
            for error in errors
        )

    def test_schedule_base_validation_schedule_date_required(self):
        """測試 ScheduleBase schedule_date 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(
                giver_id=1,
                start_time=time(9, 0),
                end_time=time(10, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "date" in str(error["loc"])
            for error in errors
        )

    def test_schedule_base_validation_start_time_required(self):
        """測試 ScheduleBase start_time 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(
                giver_id=1,
                date=date(2024, 1, 15),  # 使用別名
                end_time=time(10, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "start_time" in str(error["loc"])
            for error in errors
        )

    def test_schedule_base_validation_end_time_required(self):
        """測試 ScheduleBase end_time 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(
                giver_id=1,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "end_time" in str(error["loc"])
            for error in errors
        )

    def test_schedule_base_validation_note_max_length(self):
        """測試 ScheduleBase note 最大長度驗證。"""
        long_note = "a" * 256  # 超過 255 字元限制

        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(
                giver_id=1,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                end_time=time(10, 0),
                note=long_note,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "string_too_long" and "note" in str(error["loc"])
            for error in errors
        )

    def test_schedule_base_validation_note_max_length_boundary(self):
        """測試 ScheduleBase note 最大長度邊界值。"""
        max_note = "a" * 255  # 正好 255 字元

        schedule = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
            note=max_note,
        )

        assert schedule.note == max_note

    def test_schedule_base_with_alias(self):
        """測試 ScheduleBase 使用別名 date。"""
        schedule = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        assert schedule.schedule_date == date(2024, 1, 15)

    def test_schedule_base_model_dump(self):
        """測試 ScheduleBase model_dump 方法。"""
        schedule = ScheduleBase(
            giver_id=1,
            taker_id=2,
            status=ScheduleStatusEnum.AVAILABLE,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
        )

        data = schedule.model_dump()
        assert data["giver_id"] == 1
        assert data["taker_id"] == 2
        assert data["status"] == ScheduleStatusEnum.AVAILABLE
        assert data["schedule_date"] == date(2024, 1, 15)
        assert data["start_time"] == time(9, 0)
        assert data["end_time"] == time(10, 0)
        assert data["note"] == "測試時段"

    def test_schedule_base_model_dump_with_alias(self):
        """測試 ScheduleBase model_dump 使用別名。"""
        schedule = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        data = schedule.model_dump(by_alias=True)
        assert "date" in data
        assert "schedule_date" not in data
        assert data["date"] == date(2024, 1, 15)


class TestScheduleUpdateBase:
    """ScheduleUpdateBase 模型測試類別。"""

    def test_schedule_update_base_creation_success(self):
        """測試 ScheduleUpdateBase 建立成功情況。"""
        update = ScheduleUpdateBase(
            giver_id=1,
            taker_id=2,
            status=ScheduleStatusEnum.AVAILABLE,
            date=date(2024, 1, 16),  # 使用別名
            start_time=time(14, 0),
            end_time=time(15, 0),
            note="更新備註",
        )

        assert update.giver_id == 1
        assert update.taker_id == 2
        assert update.status == ScheduleStatusEnum.AVAILABLE
        assert update.schedule_date == date(2024, 1, 16)
        assert update.start_time == time(14, 0)
        assert update.end_time == time(15, 0)
        assert update.note == "更新備註"

    def test_schedule_update_base_creation_empty(self):
        """測試 ScheduleUpdateBase 空建立。"""
        update = ScheduleUpdateBase()

        assert update.giver_id is None
        assert update.taker_id is None
        assert update.status is None
        assert update.schedule_date is None
        assert update.start_time is None
        assert update.end_time is None
        assert update.note is None

    def test_schedule_update_base_validation_giver_id_positive(self):
        """測試 ScheduleUpdateBase giver_id 必須為正數。"""
        # ScheduleUpdateBase 的 giver_id 欄位有 gt=0 驗證，所以不能接受 0
        with pytest.raises(ValidationError) as exc_info:
            ScheduleUpdateBase(giver_id=0)

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "greater_than" and "giver_id" in str(error["loc"])
            for error in errors
        )

        # 可以接受正數
        update = ScheduleUpdateBase(giver_id=1)
        assert update.giver_id == 1

        # 不能接受負數
        with pytest.raises(ValidationError) as exc_info:
            ScheduleUpdateBase(giver_id=-1)

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "greater_than" and "giver_id" in str(error["loc"])
            for error in errors
        )

    def test_schedule_update_base_validation_note_max_length(self):
        """測試 ScheduleUpdateBase note 最大長度驗證。"""
        long_note = "a" * 256  # 超過 255 字元限制

        with pytest.raises(ValidationError) as exc_info:
            ScheduleUpdateBase(note=long_note)

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "string_too_long" and "note" in str(error["loc"])
            for error in errors
        )

    def test_schedule_update_base_with_alias(self):
        """測試 ScheduleUpdateBase 使用別名 date。"""
        update = ScheduleUpdateBase(date=date(2024, 1, 16))  # 使用別名

        assert update.schedule_date == date(2024, 1, 16)

    def test_schedule_update_base_model_dump_exclude_none(self):
        """測試 ScheduleUpdateBase model_dump 排除 None 值。"""
        update = ScheduleUpdateBase(
            giver_id=1,
            status=ScheduleStatusEnum.AVAILABLE,
            note="更新備註",
        )

        data = update.model_dump(exclude_none=True)
        assert "giver_id" in data
        assert "status" in data
        assert "note" in data
        assert "taker_id" not in data
        assert "schedule_date" not in data
        assert "start_time" not in data
        assert "end_time" not in data


class TestScheduleCreateRequest:
    """ScheduleCreateRequest 模型測試類別。"""

    def test_schedule_create_request_creation_success(self):
        """測試 ScheduleCreateRequest 建立成功情況。"""
        schedule = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        request = ScheduleCreateRequest(
            schedules=[schedule],
            created_by=1,
            created_by_role=UserRoleEnum.GIVER,
        )

        assert len(request.schedules) == 1
        assert request.schedules[0].giver_id == 1
        assert request.created_by == 1
        assert request.created_by_role == UserRoleEnum.GIVER

    def test_schedule_create_request_validation_schedules_required(self):
        """測試 ScheduleCreateRequest schedules 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreateRequest(
                created_by=1,
                created_by_role=UserRoleEnum.GIVER,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "schedules" in str(error["loc"])
            for error in errors
        )

    def test_schedule_create_request_validation_created_by_required(self):
        """測試 ScheduleCreateRequest created_by 必填驗證。"""
        schedule = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreateRequest(
                schedules=[schedule],
                created_by_role=UserRoleEnum.GIVER,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "created_by" in str(error["loc"])
            for error in errors
        )

    def test_schedule_create_request_validation_created_by_positive(self):
        """測試 ScheduleCreateRequest created_by 必須為正數。"""
        schedule = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreateRequest(
                schedules=[schedule],
                created_by=0,
                created_by_role=UserRoleEnum.GIVER,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "greater_than" and "created_by" in str(error["loc"])
            for error in errors
        )

    def test_schedule_create_request_validation_created_by_role_required(self):
        """測試 ScheduleCreateRequest created_by_role 必填驗證。"""
        schedule = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreateRequest(
                schedules=[schedule],
                created_by=1,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "created_by_role" in str(error["loc"])
            for error in errors
        )

    def test_schedule_create_request_multiple_schedules(self):
        """測試 ScheduleCreateRequest 多個時段。"""
        schedule1 = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        schedule2 = ScheduleBase(
            giver_id=1,
            date=date(2024, 1, 16),  # 使用別名
            start_time=time(14, 0),
            end_time=time(15, 0),
        )

        request = ScheduleCreateRequest(
            schedules=[schedule1, schedule2],
            created_by=1,
            created_by_role=UserRoleEnum.GIVER,
        )

        assert len(request.schedules) == 2
        assert request.schedules[0].schedule_date == date(2024, 1, 15)
        assert request.schedules[1].schedule_date == date(2024, 1, 16)


class TestSchedulePartialUpdateRequest:
    """SchedulePartialUpdateRequest 模型測試類別。"""

    def test_schedule_partial_update_request_creation_success(self):
        """測試 SchedulePartialUpdateRequest 建立成功情況。"""
        schedule = ScheduleUpdateBase(
            status=ScheduleStatusEnum.PENDING,
            note="更新備註",
        )

        request = SchedulePartialUpdateRequest(
            schedule=schedule,
            updated_by=1,
            updated_by_role=UserRoleEnum.TAKER,
        )

        assert request.schedule.status == ScheduleStatusEnum.PENDING
        assert request.schedule.note == "更新備註"
        assert request.updated_by == 1
        assert request.updated_by_role == UserRoleEnum.TAKER

    def test_schedule_partial_update_request_creation_empty_schedule(self):
        """測試 SchedulePartialUpdateRequest 空時段更新。"""
        schedule = ScheduleUpdateBase()

        request = SchedulePartialUpdateRequest(
            schedule=schedule,
            updated_by=1,
            updated_by_role=UserRoleEnum.TAKER,
        )

        assert request.schedule.giver_id is None
        assert request.schedule.status is None
        assert request.updated_by == 1
        assert request.updated_by_role == UserRoleEnum.TAKER

    def test_schedule_partial_update_request_validation_schedule_required(self):
        """測試 SchedulePartialUpdateRequest schedule 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            SchedulePartialUpdateRequest(
                updated_by=1,
                updated_by_role=UserRoleEnum.TAKER,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "schedule" in str(error["loc"])
            for error in errors
        )

    def test_schedule_partial_update_request_validation_updated_by_required(self):
        """測試 SchedulePartialUpdateRequest updated_by 必填驗證。"""
        schedule = ScheduleUpdateBase()

        with pytest.raises(ValidationError) as exc_info:
            SchedulePartialUpdateRequest(
                schedule=schedule,
                updated_by_role=UserRoleEnum.TAKER,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "updated_by" in str(error["loc"])
            for error in errors
        )

    def test_schedule_partial_update_request_validation_updated_by_positive(self):
        """測試 SchedulePartialUpdateRequest updated_by 必須為正數。"""
        schedule = ScheduleUpdateBase()

        with pytest.raises(ValidationError) as exc_info:
            SchedulePartialUpdateRequest(
                schedule=schedule,
                updated_by=0,
                updated_by_role=UserRoleEnum.TAKER,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "greater_than" and "updated_by" in str(error["loc"])
            for error in errors
        )

    def test_schedule_partial_update_request_validation_updated_by_role_required(self):
        """測試 SchedulePartialUpdateRequest updated_by_role 必填驗證。"""
        schedule = ScheduleUpdateBase()

        with pytest.raises(ValidationError) as exc_info:
            SchedulePartialUpdateRequest(
                schedule=schedule,
                updated_by=1,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "updated_by_role" in str(error["loc"])
            for error in errors
        )


class TestScheduleDeleteRequest:
    """ScheduleDeleteRequest 模型測試類別。"""

    def test_schedule_delete_request_creation_success(self):
        """測試 ScheduleDeleteRequest 建立成功情況。"""
        request = ScheduleDeleteRequest(
            deleted_by=1,
            deleted_by_role=UserRoleEnum.GIVER,
        )

        assert request.deleted_by == 1
        assert request.deleted_by_role == UserRoleEnum.GIVER

    def test_schedule_delete_request_validation_deleted_by_required(self):
        """測試 ScheduleDeleteRequest deleted_by 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleDeleteRequest(
                deleted_by_role=UserRoleEnum.GIVER,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "deleted_by" in str(error["loc"])
            for error in errors
        )

    def test_schedule_delete_request_validation_deleted_by_positive(self):
        """測試 ScheduleDeleteRequest deleted_by 必須為正數。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleDeleteRequest(
                deleted_by=0,
                deleted_by_role=UserRoleEnum.GIVER,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "greater_than" and "deleted_by" in str(error["loc"])
            for error in errors
        )

    def test_schedule_delete_request_validation_deleted_by_role_required(self):
        """測試 ScheduleDeleteRequest deleted_by_role 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleDeleteRequest(
                deleted_by=1,
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "deleted_by_role" in str(error["loc"])
            for error in errors
        )


class TestScheduleResponse:
    """ScheduleResponse 模型測試類別。"""

    def test_schedule_response_creation_success(self):
        """測試 ScheduleResponse 建立成功情況。"""
        response = ScheduleResponse(
            id=1,
            giver_id=1,
            taker_id=2,
            status=ScheduleStatusEnum.AVAILABLE,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
            created_at=datetime(2024, 1, 15, 9, 0),
            created_by=1,
            created_by_role=UserRoleEnum.GIVER,
            updated_at=datetime(2024, 1, 15, 9, 0),
            updated_by=1,
            updated_by_role=UserRoleEnum.GIVER,
            deleted_at=None,
            deleted_by=None,
            deleted_by_role=None,
        )

        assert response.id == 1
        assert response.giver_id == 1
        assert response.taker_id == 2
        assert response.status == ScheduleStatusEnum.AVAILABLE
        assert response.schedule_date == date(2024, 1, 15)
        assert response.start_time == time(9, 0)
        assert response.end_time == time(10, 0)
        assert response.note == "測試時段"
        assert response.created_at == datetime(2024, 1, 15, 9, 0)
        assert response.created_by == 1
        assert response.created_by_role == UserRoleEnum.GIVER
        assert response.updated_at == datetime(2024, 1, 15, 9, 0)
        assert response.updated_by == 1
        assert response.updated_by_role == UserRoleEnum.GIVER
        assert response.deleted_at is None
        assert response.deleted_by is None
        assert response.deleted_by_role is None

    def test_schedule_response_creation_with_minimal_data(self):
        """測試 ScheduleResponse 使用最少資料建立。"""
        response = ScheduleResponse(
            id=1,
            giver_id=1,
            status=ScheduleStatusEnum.DRAFT,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
            created_at=datetime(2024, 1, 15, 9, 0),
            updated_at=datetime(2024, 1, 15, 9, 0),
        )

        assert response.id == 1
        assert response.giver_id == 1
        assert response.taker_id is None
        assert response.status == ScheduleStatusEnum.DRAFT
        assert response.note is None
        assert response.created_by is None
        assert response.created_by_role is None
        assert response.updated_by is None
        assert response.updated_by_role is None
        assert response.deleted_at is None
        assert response.deleted_by is None
        assert response.deleted_by_role is None

    def test_schedule_response_validation_id_required(self):
        """測試 ScheduleResponse id 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                giver_id=1,
                status=ScheduleStatusEnum.DRAFT,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                end_time=time(10, 0),
                created_at=datetime(2024, 1, 15, 9, 0),
                updated_at=datetime(2024, 1, 15, 9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "id" in str(error["loc"]) for error in errors
        )

    def test_schedule_response_validation_id_positive(self):
        """測試 ScheduleResponse id 必須為正數。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                id=0,
                giver_id=1,
                status=ScheduleStatusEnum.DRAFT,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                end_time=time(10, 0),
                created_at=datetime(2024, 1, 15, 9, 0),
                updated_at=datetime(2024, 1, 15, 9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "greater_than" and "id" in str(error["loc"])
            for error in errors
        )

    def test_schedule_response_validation_giver_id_required(self):
        """測試 ScheduleResponse giver_id 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                id=1,
                status=ScheduleStatusEnum.DRAFT,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                end_time=time(10, 0),
                created_at=datetime(2024, 1, 15, 9, 0),
                updated_at=datetime(2024, 1, 15, 9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "giver_id" in str(error["loc"])
            for error in errors
        )

    def test_schedule_response_validation_giver_id_positive(self):
        """測試 ScheduleResponse giver_id 必須為正數。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                id=1,
                giver_id=0,
                status=ScheduleStatusEnum.DRAFT,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                end_time=time(10, 0),
                created_at=datetime(2024, 1, 15, 9, 0),
                updated_at=datetime(2024, 1, 15, 9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "greater_than" and "giver_id" in str(error["loc"])
            for error in errors
        )

    def test_schedule_response_validation_status_required(self):
        """測試 ScheduleResponse status 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                id=1,
                giver_id=1,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                end_time=time(10, 0),
                created_at=datetime(2024, 1, 15, 9, 0),
                updated_at=datetime(2024, 1, 15, 9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "status" in str(error["loc"])
            for error in errors
        )

    def test_schedule_response_validation_schedule_date_required(self):
        """測試 ScheduleResponse schedule_date 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                id=1,
                giver_id=1,
                status=ScheduleStatusEnum.DRAFT,
                start_time=time(9, 0),
                end_time=time(10, 0),
                created_at=datetime(2024, 1, 15, 9, 0),
                updated_at=datetime(2024, 1, 15, 9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "date" in str(error["loc"])
            for error in errors
        )

    def test_schedule_response_validation_start_time_required(self):
        """測試 ScheduleResponse start_time 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                id=1,
                giver_id=1,
                status=ScheduleStatusEnum.DRAFT,
                date=date(2024, 1, 15),  # 使用別名
                end_time=time(10, 0),
                created_at=datetime(2024, 1, 15, 9, 0),
                updated_at=datetime(2024, 1, 15, 9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "start_time" in str(error["loc"])
            for error in errors
        )

    def test_schedule_response_validation_end_time_required(self):
        """測試 ScheduleResponse end_time 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                id=1,
                giver_id=1,
                status=ScheduleStatusEnum.DRAFT,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                created_at=datetime(2024, 1, 15, 9, 0),
                updated_at=datetime(2024, 1, 15, 9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "end_time" in str(error["loc"])
            for error in errors
        )

    def test_schedule_response_validation_created_at_required(self):
        """測試 ScheduleResponse created_at 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                id=1,
                giver_id=1,
                status=ScheduleStatusEnum.DRAFT,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                end_time=time(10, 0),
                updated_at=datetime(2024, 1, 15, 9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "created_at" in str(error["loc"])
            for error in errors
        )

    def test_schedule_response_validation_updated_at_required(self):
        """測試 ScheduleResponse updated_at 必填驗證。"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                id=1,
                giver_id=1,
                status=ScheduleStatusEnum.DRAFT,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                end_time=time(10, 0),
                created_at=datetime(2024, 1, 15, 9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and "updated_at" in str(error["loc"])
            for error in errors
        )

    def test_schedule_response_validation_note_max_length(self):
        """測試 ScheduleResponse note 最大長度驗證。"""
        long_note = "a" * 256  # 超過 255 字元限制

        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                id=1,
                giver_id=1,
                status=ScheduleStatusEnum.DRAFT,
                date=date(2024, 1, 15),  # 使用別名
                start_time=time(9, 0),
                end_time=time(10, 0),
                note=long_note,
                created_at=datetime(2024, 1, 15, 9, 0),
                updated_at=datetime(2024, 1, 15, 9, 0),
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "string_too_long" and "note" in str(error["loc"])
            for error in errors
        )

    def test_schedule_response_with_alias(self):
        """測試 ScheduleResponse 使用別名 date。"""
        response = ScheduleResponse(
            id=1,
            giver_id=1,
            status=ScheduleStatusEnum.DRAFT,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
            created_at=datetime(2024, 1, 15, 9, 0),
            updated_at=datetime(2024, 1, 15, 9, 0),
        )

        assert response.schedule_date == date(2024, 1, 15)

    def test_schedule_response_model_dump(self):
        """測試 ScheduleResponse model_dump 方法。"""
        response = ScheduleResponse(
            id=1,
            giver_id=1,
            taker_id=2,
            status=ScheduleStatusEnum.AVAILABLE,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
            note="測試時段",
            created_at=datetime(2024, 1, 15, 9, 0),
            created_by=1,
            created_by_role=UserRoleEnum.GIVER,
            updated_at=datetime(2024, 1, 15, 9, 0),
            updated_by=1,
            updated_by_role=UserRoleEnum.GIVER,
            deleted_at=None,
            deleted_by=None,
            deleted_by_role=None,
        )

        data = response.model_dump()
        assert data["id"] == 1
        assert data["giver_id"] == 1
        assert data["taker_id"] == 2
        assert data["status"] == ScheduleStatusEnum.AVAILABLE
        assert data["schedule_date"] == date(2024, 1, 15)
        assert data["start_time"] == time(9, 0)
        assert data["end_time"] == time(10, 0)
        assert data["note"] == "測試時段"
        assert data["created_at"] == datetime(2024, 1, 15, 9, 0)
        assert data["created_by"] == 1
        assert data["created_by_role"] == UserRoleEnum.GIVER
        assert data["updated_at"] == datetime(2024, 1, 15, 9, 0)
        assert data["updated_by"] == 1
        assert data["updated_by_role"] == UserRoleEnum.GIVER
        assert data["deleted_at"] is None
        assert data["deleted_by"] is None
        assert data["deleted_by_role"] is None

    def test_schedule_response_model_dump_with_alias(self):
        """測試 ScheduleResponse model_dump 使用別名。"""
        response = ScheduleResponse(
            id=1,
            giver_id=1,
            status=ScheduleStatusEnum.DRAFT,
            date=date(2024, 1, 15),  # 使用別名
            start_time=time(9, 0),
            end_time=time(10, 0),
            created_at=datetime(2024, 1, 15, 9, 0),
            updated_at=datetime(2024, 1, 15, 9, 0),
        )

        data = response.model_dump(by_alias=True)
        assert "date" in data
        assert "schedule_date" not in data
        assert data["date"] == date(2024, 1, 15)

    def test_schedule_response_model_validate(self):
        """測試 ScheduleResponse model_validate 方法。"""
        data = {
            "id": 1,
            "giver_id": 1,
            "taker_id": 2,
            "status": ScheduleStatusEnum.AVAILABLE,
            "schedule_date": date(2024, 1, 15),
            "start_time": time(9, 0),
            "end_time": time(10, 0),
            "note": "測試時段",
            "created_at": datetime(2024, 1, 15, 9, 0),
            "created_by": 1,
            "created_by_role": UserRoleEnum.GIVER,
            "updated_at": datetime(2024, 1, 15, 9, 0),
            "updated_by": 1,
            "updated_by_role": UserRoleEnum.GIVER,
            "deleted_at": None,
            "deleted_by": None,
            "deleted_by_role": None,
        }

        response = ScheduleResponse.model_validate(data)
        assert response.id == 1
        assert response.giver_id == 1
        assert response.taker_id == 2
        assert response.status == ScheduleStatusEnum.AVAILABLE
        assert response.schedule_date == date(2024, 1, 15)
        assert response.start_time == time(9, 0)
        assert response.end_time == time(10, 0)
        assert response.note == "測試時段"

    def test_schedule_response_model_validate_with_alias(self):
        """測試 ScheduleResponse model_validate 使用別名。"""
        data = {
            "id": 1,
            "giver_id": 1,
            "status": ScheduleStatusEnum.DRAFT,
            "date": date(2024, 1, 15),  # 使用別名
            "start_time": time(9, 0),
            "end_time": time(10, 0),
            "created_at": datetime(2024, 1, 15, 9, 0),
            "updated_at": datetime(2024, 1, 15, 9, 0),
        }

        response = ScheduleResponse.model_validate(data)
        assert response.schedule_date == date(2024, 1, 15)

    def test_schedule_response_config_dict(self):
        """測試 ScheduleResponse 配置字典。"""
        config = ScheduleResponse.model_config
        assert config["from_attributes"] is True
        assert config["populate_by_name"] is True
