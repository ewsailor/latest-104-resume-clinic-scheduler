"""
Schema 整合測試模組。

測試 Pydantic 資料模型的驗證、序列化和反序列化功能。
"""

# ===== 標準函式庫 =====
import datetime
from typing import Any, Dict

# ===== 第三方套件 =====
from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from app.enums.models import ScheduleStatusEnum, UserRoleEnum

# ===== 本地模組 =====
from app.main import app
from app.schemas.schedule import (
    ScheduleBase,
    ScheduleCreateRequest,
    ScheduleDeleteRequest,
    SchedulePartialUpdateRequest,
    ScheduleResponse,
    ScheduleUpdateBase,
    ScheduleUpdateRequest,
)
from tests.utils.test_utils import generate_unique_time_slot


class TestScheduleSchemaIntegration:
    """Schedule Schema 整合測試類別。"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端。"""
        return TestClient(app)

    @pytest.fixture
    def valid_schedule_data(self) -> Dict[str, Any]:
        """提供有效的時段資料。"""
        date, start_time, end_time = generate_unique_time_slot()
        return {
            "giver_id": 1,
            "taker_id": 2,
            "status": "AVAILABLE",
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "note": "測試備註",
        }

    def test_schedule_base_validation_success(
        self, valid_schedule_data: Dict[str, Any]
    ):
        """測試 ScheduleBase 模型驗證成功。"""
        schedule = ScheduleBase(**valid_schedule_data)

        assert schedule.giver_id == 1
        assert schedule.taker_id == 2
        assert schedule.status == ScheduleStatusEnum.AVAILABLE
        assert schedule.schedule_date == datetime.date.fromisoformat(
            valid_schedule_data["date"]
        )
        assert schedule.start_time == datetime.time.fromisoformat(
            valid_schedule_data["start_time"]
        )
        assert schedule.end_time == datetime.time.fromisoformat(
            valid_schedule_data["end_time"]
        )
        assert schedule.note == "測試備註"

    def test_schedule_base_validation_failure(self):
        """測試 ScheduleBase 模型驗證失敗。"""
        # 測試缺少必要欄位
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(giver_id=1)

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error["type"] == "missing" for error in errors)

        # 測試無效的 giver_id
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(
                giver_id=0,  # 應該 > 0
                date="2025-09-15",
                start_time="09:00:00",
                end_time="10:00:00",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "greater_than" for error in errors)

        # 測試無效的狀態
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(
                giver_id=1,
                status="INVALID_STATUS",
                date="2025-09-15",
                start_time="09:00:00",
                end_time="10:00:00",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "enum" for error in errors)

        # 測試無效的日期格式
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(
                giver_id=1,
                date="invalid-date",
                start_time="09:00:00",
                end_time="10:00:00",
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"]
            in ["date_from_iso_format", "date_type", "date_from_datetime_parsing"]
            for error in errors
        )

        # 測試無效的時間格式
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(
                giver_id=1,
                date="2025-09-15",
                start_time="invalid-time",
                end_time="10:00:00",
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] in ["time_from_iso_format", "time_parsing"]
            for error in errors
        )

        # 測試備註長度超限
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(
                giver_id=1,
                date="2025-09-15",
                start_time="09:00:00",
                end_time="10:00:00",
                note="x" * 256,  # 超過 255 字元限制
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)

    def test_schedule_update_base_validation(self):
        """測試 ScheduleUpdateBase 模型驗證。"""
        # 測試所有欄位都是可選的
        schedule = ScheduleUpdateBase()
        assert schedule.giver_id is None
        assert schedule.taker_id is None
        assert schedule.status is None
        assert schedule.schedule_date is None
        assert schedule.start_time is None
        assert schedule.end_time is None
        assert schedule.note is None

        # 測試部分更新
        schedule = ScheduleUpdateBase(
            status=ScheduleStatusEnum.PENDING, note="更新備註"
        )
        assert schedule.status == ScheduleStatusEnum.PENDING
        assert schedule.note == "更新備註"
        assert schedule.giver_id is None

    def test_schedule_create_request_validation(
        self, valid_schedule_data: Dict[str, Any]
    ):
        """測試 ScheduleCreateRequest 模型驗證。"""
        request_data = {
            "schedules": [valid_schedule_data],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        request = ScheduleCreateRequest(**request_data)

        assert len(request.schedules) == 1
        assert request.schedules[0].giver_id == 1
        assert request.created_by == 1
        assert request.created_by_role == UserRoleEnum.GIVER

    def test_schedule_create_request_validation_failure(self):
        """測試 ScheduleCreateRequest 模型驗證失敗。"""
        # 測試空的時段列表 - 實際上空的列表是允許的，所以我們測試其他驗證錯誤
        # 測試無效的 created_by
        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreateRequest(
                schedules=[
                    {
                        "giver_id": 1,
                        "date": "2025-09-15",
                        "start_time": "09:00:00",
                        "end_time": "10:00:00",
                    }
                ],
                created_by=0,  # 應該 > 0
                created_by_role="GIVER",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "greater_than" for error in errors)

    def test_schedule_update_request_validation(
        self, valid_schedule_data: Dict[str, Any]
    ):
        """測試 ScheduleUpdateRequest 模型驗證。"""
        request_data = {
            "schedule": valid_schedule_data,
            "updated_by": 1,
            "updated_by_role": "TAKER",
        }

        request = ScheduleUpdateRequest(**request_data)

        assert request.schedule.giver_id == 1
        assert request.updated_by == 1
        assert request.updated_by_role == UserRoleEnum.TAKER

    def test_schedule_partial_update_request_validation(self):
        """測試 SchedulePartialUpdateRequest 模型驗證。"""
        request_data = {
            "schedule": {
                "status": "PENDING",
                "note": "部分更新備註",
            },
            "updated_by": 1,
            "updated_by_role": "TAKER",
        }

        request = SchedulePartialUpdateRequest(**request_data)

        assert request.schedule.status == ScheduleStatusEnum.PENDING
        assert request.schedule.note == "部分更新備註"
        assert request.schedule.giver_id is None  # 未提供
        assert request.updated_by == 1
        assert request.updated_by_role == UserRoleEnum.TAKER

    def test_schedule_delete_request_validation(self):
        """測試 ScheduleDeleteRequest 模型驗證。"""
        request_data = {
            "deleted_by": 1,
            "deleted_by_role": "GIVER",
        }

        request = ScheduleDeleteRequest(**request_data)

        assert request.deleted_by == 1
        assert request.deleted_by_role == UserRoleEnum.GIVER

    def test_schedule_delete_request_validation_failure(self):
        """測試 ScheduleDeleteRequest 模型驗證失敗。"""
        # 測試無效的 deleted_by
        with pytest.raises(ValidationError) as exc_info:
            ScheduleDeleteRequest(
                deleted_by=0,  # 應該 > 0
                deleted_by_role="GIVER",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "greater_than" for error in errors)

    def test_schedule_response_validation(self, valid_schedule_data: Dict[str, Any]):
        """測試 ScheduleResponse 模型驗證。"""
        response_data = {
            "id": 1,
            "giver_id": 1,
            "taker_id": 2,
            "status": "AVAILABLE",
            "date": valid_schedule_data["date"],
            "start_time": valid_schedule_data["start_time"],
            "end_time": valid_schedule_data["end_time"],
            "note": "測試備註",
            "created_at": "2025-09-15T09:00:00",
            "created_by": 1,
            "created_by_role": "GIVER",
            "updated_at": "2025-09-15T09:00:00",
            "updated_by": 1,
            "updated_by_role": "GIVER",
            "deleted_at": None,
            "deleted_by": None,
            "deleted_by_role": None,
        }

        response = ScheduleResponse(**response_data)

        assert response.id == 1
        assert response.giver_id == 1
        assert response.taker_id == 2
        assert response.status == ScheduleStatusEnum.AVAILABLE
        assert response.schedule_date == datetime.date.fromisoformat(
            valid_schedule_data["date"]
        )
        assert response.start_time == datetime.time.fromisoformat(
            valid_schedule_data["start_time"]
        )
        assert response.end_time == datetime.time.fromisoformat(
            valid_schedule_data["end_time"]
        )
        assert response.note == "測試備註"
        assert response.created_at == datetime.datetime.fromisoformat(
            "2025-09-15T09:00:00"
        )
        assert response.created_by == 1
        assert response.created_by_role == UserRoleEnum.GIVER
        assert response.updated_at == datetime.datetime.fromisoformat(
            "2025-09-15T09:00:00"
        )
        assert response.updated_by == 1
        assert response.updated_by_role == UserRoleEnum.GIVER
        assert response.deleted_at is None
        assert response.deleted_by is None
        assert response.deleted_by_role is None

    def test_schedule_response_validation_failure(self):
        """測試 ScheduleResponse 模型驗證失敗。"""
        # 測試缺少必要欄位
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(id=1)

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error["type"] == "missing" for error in errors)

        # 測試無效的 ID
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponse(
                id=0,  # 應該 > 0
                giver_id=1,
                status="AVAILABLE",
                date="2025-09-15",
                start_time="09:00:00",
                end_time="10:00:00",
                created_at="2025-09-15T09:00:00",
                updated_at="2025-09-15T09:00:00",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "greater_than" for error in errors)

    def test_schema_serialization_and_deserialization(
        self, valid_schedule_data: Dict[str, Any]
    ):
        """測試 Schema 的序列化和反序列化。"""
        # 測試 ScheduleBase 的序列化
        schedule = ScheduleBase(**valid_schedule_data)
        serialized = schedule.model_dump()

        assert isinstance(serialized, dict)
        assert serialized["giver_id"] == 1
        assert serialized["taker_id"] == 2
        assert serialized["status"] == "AVAILABLE"
        # 序列化後使用 schedule_date 而不是 date
        assert "schedule_date" in serialized
        assert "date" not in serialized

        # 測試反序列化 - 需要將 schedule_date 轉換為 date 別名
        serialized_with_alias = serialized.copy()
        serialized_with_alias["date"] = serialized_with_alias.pop("schedule_date")
        deserialized = ScheduleBase(**serialized_with_alias)
        assert deserialized.giver_id == schedule.giver_id
        assert deserialized.taker_id == schedule.taker_id
        assert deserialized.status == schedule.status

    def test_schema_json_serialization(self, valid_schedule_data: Dict[str, Any]):
        """測試 Schema 的 JSON 序列化。"""
        schedule = ScheduleBase(**valid_schedule_data)
        json_str = schedule.model_dump_json()

        assert isinstance(json_str, str)
        assert '"giver_id":1' in json_str
        assert '"status":"AVAILABLE"' in json_str
        # JSON 序列化後使用 schedule_date 而不是 date
        assert '"schedule_date"' in json_str
        assert '"date"' not in json_str

        # 測試從 JSON 反序列化 - 需要處理別名問題
        import json

        json_data = json.loads(json_str)
        json_data["date"] = json_data.pop("schedule_date")
        from_json = ScheduleBase(**json_data)
        assert from_json.giver_id == schedule.giver_id
        assert from_json.status == schedule.status

    def test_schema_alias_handling(self, valid_schedule_data: Dict[str, Any]):
        """測試 Schema 的別名處理。"""
        # 測試使用別名 "date" 而不是 "schedule_date"
        data_with_alias = valid_schedule_data.copy()
        # 確保使用正確的別名
        if "schedule_date" in data_with_alias:
            data_with_alias["date"] = data_with_alias.pop("schedule_date")

        schedule = ScheduleBase(**data_with_alias)
        assert schedule.schedule_date == datetime.date.fromisoformat(
            valid_schedule_data["date"]
        )

        # 測試序列化時使用別名
        serialized = schedule.model_dump(by_alias=True)
        assert "date" in serialized
        assert "schedule_date" not in serialized

    def test_schema_enum_validation(self):
        """測試 Schema 的枚舉驗證。"""
        # 測試有效的狀態值
        valid_statuses = [
            "DRAFT",
            "AVAILABLE",
            "PENDING",
            "ACCEPTED",
            "REJECTED",
            "CANCELLED",
            "COMPLETED",
        ]
        for status in valid_statuses:
            schedule = ScheduleBase(
                giver_id=1,
                status=status,
                date="2025-09-15",
                start_time="09:00:00",
                end_time="10:00:00",
            )
            assert schedule.status == ScheduleStatusEnum(status)

        # 測試有效的角色值
        valid_roles = ["GIVER", "TAKER", "SYSTEM"]  # 根據實際的 UserRoleEnum 值
        for role in valid_roles:
            request = ScheduleCreateRequest(
                schedules=[
                    {
                        "giver_id": 1,
                        "date": "2025-09-15",
                        "start_time": "09:00:00",
                        "end_time": "10:00:00",
                    }
                ],
                created_by=1,
                created_by_role=role,
            )
            assert request.created_by_role == UserRoleEnum(role)

    def test_schema_optional_fields_handling(self):
        """測試 Schema 的可選欄位處理。"""
        # 測試 taker_id 為 None
        schedule = ScheduleBase(
            giver_id=1,
            taker_id=None,
            date="2025-09-15",
            start_time="09:00:00",
            end_time="10:00:00",
        )
        assert schedule.taker_id is None

        # 測試 note 為 None
        schedule = ScheduleBase(
            giver_id=1,
            date="2025-09-15",
            start_time="09:00:00",
            end_time="10:00:00",
            note=None,
        )
        assert schedule.note is None

        # 測試不提供可選欄位
        schedule = ScheduleBase(
            giver_id=1,
            date="2025-09-15",
            start_time="09:00:00",
            end_time="10:00:00",
        )
        assert schedule.taker_id is None
        assert schedule.note is None

    def test_schema_model_config(self):
        """測試 Schema 的模型配置。"""
        # 測試 ConfigDict 的配置
        schedule = ScheduleBase(
            giver_id=1,
            date="2025-09-15",
            start_time="09:00:00",
            end_time="10:00:00",
        )

        # 測試 model_dump 方法
        data = schedule.model_dump()
        assert isinstance(data, dict)

        # 測試 model_dump_json 方法
        json_data = schedule.model_dump_json()
        assert isinstance(json_data, str)

        # 測試 model_validate 方法 - 需要處理別名問題
        data_with_alias = data.copy()
        data_with_alias["date"] = data_with_alias.pop("schedule_date")
        validated = ScheduleBase.model_validate(data_with_alias)
        assert validated.giver_id == schedule.giver_id

    def test_schema_integration_with_api(
        self, client: TestClient, valid_schedule_data: Dict[str, Any]
    ):
        """測試 Schema 與 API 的整合。"""
        # 測試建立時段請求的 Schema 驗證
        create_request = {
            "schedules": [valid_schedule_data],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        # 驗證請求資料符合 Schema
        validated_request = ScheduleCreateRequest(**create_request)
        assert len(validated_request.schedules) == 1

        # 測試 API 端點接受有效的 Schema
        response = client.post("/api/v1/schedules", json=create_request)
        assert response.status_code == 201

        # 驗證回應資料符合 Schema
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 1

        # 驗證回應中的每個時段都符合 ScheduleResponse Schema
        for schedule_data in response_data:
            validated_response = ScheduleResponse(**schedule_data)
            assert validated_response.id > 0
            assert validated_response.giver_id == 1
            assert validated_response.status in ScheduleStatusEnum

    def test_schema_validation_error_handling(self, client: TestClient):
        """測試 Schema 驗證錯誤的處理。"""
        # 測試無效的請求資料
        invalid_request = {
            "schedules": [
                {
                    "giver_id": 0,  # 無效的 giver_id
                    "date": "invalid-date",  # 無效的日期
                    "start_time": "invalid-time",  # 無效的時間
                    "end_time": "10:00:00",
                }
            ],
            "created_by": 0,  # 無效的 created_by
            "created_by_role": "INVALID_ROLE",  # 無效的角色
        }

        response = client.post("/api/v1/schedules", json=invalid_request)
        assert response.status_code == 422  # 驗證錯誤

        # 驗證錯誤回應格式
        error_data = response.json()
        assert "detail" in error_data
        assert isinstance(error_data["detail"], list)
        assert len(error_data["detail"]) > 0

    def test_schema_partial_update_validation(
        self, client: TestClient, valid_schedule_data: Dict[str, Any]
    ):
        """測試部分更新請求的 Schema 驗證。"""
        # 先建立一個時段
        create_request = {
            "schedules": [valid_schedule_data],
            "created_by": 1,
            "created_by_role": "GIVER",
        }

        create_response = client.post("/api/v1/schedules", json=create_request)
        assert create_response.status_code == 201

        schedule_id = create_response.json()[0]["id"]

        # 測試部分更新請求
        update_request = {
            "schedule": {
                "status": "PENDING",
                "note": "更新備註",
            },
            "updated_by": 1,
            "updated_by_role": "TAKER",
        }

        # 驗證請求資料符合 Schema
        validated_request = SchedulePartialUpdateRequest(**update_request)
        assert validated_request.schedule.status == ScheduleStatusEnum.PENDING
        assert validated_request.schedule.note == "更新備註"
        assert validated_request.updated_by == 1
        assert validated_request.updated_by_role == UserRoleEnum.TAKER

        # 測試 API 端點接受有效的部分更新請求
        response = client.patch(f"/api/v1/schedules/{schedule_id}", json=update_request)
        assert response.status_code == 200

        # 驗證回應資料符合 Schema
        response_data = response.json()
        validated_response = ScheduleResponse(**response_data)
        assert validated_response.status == ScheduleStatusEnum.PENDING
        assert validated_response.note == "更新備註"
