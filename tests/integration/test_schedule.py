"""時段路由整合測試。

測試時段管理 API 的完整流程，包括建立、查詢、更新和刪除時段。
"""

from datetime import date, time

# ===== 標準函式庫 =====
import json

# ===== 第三方套件 =====
from fastapi import status
import pytest

# ===== 本地模組 =====
from app.enums.models import ScheduleStatusEnum
from app.models.schedule import Schedule as ScheduleModel


class TestScheduleRoutes:
    """時段路由整合測試類別。"""

    @pytest.fixture
    def client(self, integration_test_client):
        """建立測試客戶端。"""
        return integration_test_client

    # ===== 建立時段 =====
    def test_create_schedules_success(
        self, client, integration_db_session, schedule_create_payload
    ):
        """測試建立時段 - 成功。"""
        # GIVEN：使用 fixture 提供的資料

        # WHEN：呼叫建立時段 API
        response = client.post("/api/v1/schedules", json=schedule_create_payload)

        # THEN：確認建立成功
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()  # 轉成 Python 物件
        assert isinstance(data, list)  # 回傳格式是 list
        assert len(data) == 1

        # ===== 驗證回應資料結構 =====
        schedule_json = data[0]

        # 基本欄位驗證
        assert "id" in schedule_json
        assert schedule_json["giver_id"] == 1
        assert schedule_json["taker_id"] is None
        assert schedule_json["note"] == "測試時段"
        assert schedule_json["created_by"] == 1
        assert schedule_json["created_by_role"] == "GIVER"
        assert schedule_json["updated_by"] == 1
        assert schedule_json["updated_by_role"] == "GIVER"

        # JSON Response 只能存字串或數字，不能存 Python Enum 物件
        # 用 .value 取出 Python Enum 物件的值
        assert (
            schedule_json["status"] == ScheduleStatusEnum.AVAILABLE.value
        )  # GIVER 建立時段時狀態應為 AVAILABLE

        # JSON Response 中，date、time 是字串格式
        assert schedule_json["date"] == "2024-12-25"
        assert schedule_json["start_time"] == "09:00:00"
        assert schedule_json["end_time"] == "10:00:00"

        # 時間戳記驗證
        assert "created_at" in schedule_json
        assert "updated_at" in schedule_json
        assert schedule_json["created_at"] is not None
        assert schedule_json["updated_at"] is not None

        # 建立時，create 和 update 以下 3 個欄位應該相同
        assert schedule_json["created_at"] == schedule_json["updated_at"]
        assert schedule_json["created_by"] == schedule_json["updated_by"]
        assert schedule_json["created_by_role"] == schedule_json["updated_by_role"]

        # 軟刪除相關（建立時應為 null）
        assert schedule_json["deleted_at"] is None
        assert schedule_json["deleted_by"] is None
        assert schedule_json["deleted_by_role"] is None

        # ===== 查詢資料庫，驗證寫入的內容是否正確 =====
        # 從 API 回傳取得 id
        schedule_id = schedule_json["id"]

        # 查主鍵，故使用 get() 而不是 .query().filter(...).first()
        db_schedule = integration_db_session.get(ScheduleModel, schedule_id)

        # 驗證記錄存在
        assert db_schedule is not None

        # 驗證欄位值寫入正確
        assert db_schedule.id == schedule_json["id"]
        assert db_schedule.giver_id == 1
        assert db_schedule.taker_id is None
        assert db_schedule.note == "測試時段"
        assert db_schedule.created_by == 1
        assert db_schedule.created_by_role == "GIVER"
        assert db_schedule.updated_by == 1
        assert db_schedule.updated_by_role == "GIVER"

        # ORM 將資料庫中 Enum 物件，轉回 Python 的 Enum 物件，故可以直接用 Enum 比對
        assert db_schedule.status == ScheduleStatusEnum.AVAILABLE

        # 驗證 ORM 資料型別轉換
        # 1. 請求階段，API 傳入的 date、time 是 JSON 字串格式
        # 2. Pydantic schema 將 JSON 字串，轉成 Python 的 date、time 物件
        # 3. ORM 將 Python 的 date、time 物件，寫入 MySQL/MariaDB 資料庫成 DATE、TIME 物件
        # 4. 查詢資料庫時，ORM 將資料庫中 DATE、TIME 物件，轉回 Python 的 date、time 物件
        assert db_schedule.date == date(2024, 12, 25)
        assert db_schedule.start_time == time(9, 0, 0)
        assert db_schedule.end_time == time(10, 0, 0)
        # 驗證 ORM 物件轉為字串後，與原始請求一致 (JSON 格式)
        assert str(db_schedule.date) == "2024-12-25"
        assert str(db_schedule.start_time) == "09:00:00"
        assert str(db_schedule.end_time) == "10:00:00"

        # 時間戳記驗證
        assert db_schedule.created_at is not None
        assert db_schedule.updated_at is not None

        # 建立時，create 和 update 以下 3 個欄位應該相同
        assert db_schedule.created_at == db_schedule.updated_at
        assert db_schedule.created_by == db_schedule.updated_by
        assert db_schedule.created_by_role == db_schedule.updated_by_role

        # 軟刪除相關（建立時應為 null）
        assert db_schedule.deleted_at is None
        assert db_schedule.deleted_by is None
        assert db_schedule.deleted_by_role is None

    def test_create_schedules_end_before_start(self, client, schedule_create_payload):
        """測試建立時段 - 結束時間早於開始時間（400）。"""
        # GIVEN：使用夾具資料並修改為無效的時間邏輯
        invalid_payload = schedule_create_payload.copy()
        invalid_payload["schedules"][0]["start_time"] = "10:00:00"
        invalid_payload["schedules"][0]["end_time"] = "09:00:00"  # 結束時間早於開始時間

        # WHEN：呼叫建立時段 API
        response = client.post("/api/v1/schedules", json=invalid_payload)

        # THEN：確認返回時間邏輯錯誤
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "error" in data

        # 驗證錯誤回應的完整格式
        error = data["error"]
        assert error["message"] == "開始時間必須早於結束時間"
        assert error["status_code"] == 400
        assert error["code"] == "ROUTER_BAD_REQUEST"
        assert "timestamp" in error
        assert "details" in error

    def test_create_schedules_time_conflict(self, client, schedule_create_payload):
        """測試建立時段 - 時段衝突錯誤（409）。"""
        # GIVEN：先建立一個時段，然後嘗試建立重疊的時段
        # 1. 先建立第一個時段
        first_payload = schedule_create_payload.copy()
        first_payload["schedules"][0]["date"] = "2024-01-15"
        first_payload["schedules"][0]["start_time"] = "09:00:00"
        first_payload["schedules"][0]["end_time"] = "10:00:00"

        # 建立第一個時段
        first_response = client.post("/api/v1/schedules", json=first_payload)
        assert first_response.status_code == status.HTTP_201_CREATED

        # 2. 建立重疊的時段
        conflict_payload = schedule_create_payload.copy()
        conflict_payload["schedules"][0]["date"] = "2024-01-15"
        conflict_payload["schedules"][0]["start_time"] = "09:30:00"  # 與第一個時段重疊
        conflict_payload["schedules"][0]["end_time"] = "10:30:00"

        # WHEN：呼叫建立時段 API
        response = client.post("/api/v1/schedules", json=conflict_payload)

        # THEN：確認返回時段衝突錯誤
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert "error" in data

        # 驗證錯誤回應的完整格式
        error = data["error"]
        assert "檢測到" in error["message"] and "重疊時段" in error["message"]
        assert error["status_code"] == 409
        assert error["code"] == "SERVICE_SCHEDULE_OVERLAP"
        assert "timestamp" in error
        assert "details" in error
        assert "overlapping_schedules" in error["details"]

    def test_create_schedules_validation_error(self, client, schedule_create_payload):
        """測試建立時段 - 參數驗證錯誤（422）。"""
        # GIVEN：使用夾具資料並移除必填欄位
        invalid_payload = schedule_create_payload.copy()
        invalid_payload["schedules"][0].pop("date")  # 移除必填欄位創造 422 錯誤

        # WHEN：呼叫建立時段 API
        response = client.post("/api/v1/schedules", json=invalid_payload)

        # THEN：確認返回驗證錯誤
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

        # 驗證 422 錯誤的完整格式
        detail = data["detail"]
        assert isinstance(detail, list)
        assert len(detail) > 0

        # 驗證錯誤詳情的結構
        error_detail = detail[0]
        assert "type" in error_detail
        assert "loc" in error_detail
        assert "msg" in error_detail
        assert "input" in error_detail

    # ===== 查詢時段列表 =====
    def test_list_schedules_success(self, client):
        """測試查詢時段列表 - 成功。"""
        # GIVEN：資料庫中有時段資料

        # WHEN：呼叫查詢時段列表 API
        response = client.get("/api/v1/schedules")

        # THEN：確認查詢成功
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_schedules_with_filters(self, client):
        """測試查詢時段列表 - 使用篩選條件。"""
        # GIVEN：查詢參數

        # WHEN：使用篩選條件查詢時段列表
        response = client.get("/api/v1/schedules?giver_id=1&status_filter=AVAILABLE")

        # THEN：確認查詢成功
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_schedules_invalid_filters(self, client):
        """測試查詢時段列表 - 無效篩選條件。"""
        # GIVEN：無效的查詢參數（giver_id 必須大於 0）

        # WHEN：使用無效的篩選條件查詢
        response = client.get("/api/v1/schedules?giver_id=0")

        # THEN：確認返回驗證錯誤
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    # ===== 取得單一時段 =====
    def test_get_schedule_success(self, client, schedule_create_payload):
        """測試取得單一時段 - 成功。"""
        # GIVEN：先建立一個時段，使用 fixture 提供的唯一資料
        create_response = client.post("/api/v1/schedules", json=schedule_create_payload)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_schedule = create_response.json()[0]
        schedule_id = created_schedule["id"]

        # WHEN：呼叫取得單一時段 API
        response = client.get(f"/api/v1/schedules/{schedule_id}")

        # THEN：確認取得成功
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["id"] == schedule_id
        assert "giver_id" in data
        assert "date" in data
        assert "start_time" in data
        assert "end_time" in data
        assert "status" in data

    def test_get_schedule_not_found(self, client):
        """測試取得單一時段 - 時段不存在。"""
        # GIVEN：不存在的時段 ID

        # WHEN：呼叫取得單一時段 API
        response = client.get("/api/v1/schedules/99999")

        # THEN：確認返回找不到錯誤
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert "時段不存在" in data["error"]["message"]

    def test_get_schedule_invalid_id(self, client):
        """測試取得單一時段 - 無效的時段 ID。"""
        # GIVEN：無效的時段 ID（必須大於 0）

        # WHEN：使用無效的時段 ID 呼叫 API
        response = client.get("/api/v1/schedules/0")

        # THEN：確認返回驗證錯誤
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    # ===== 更新時段 =====
    def test_update_schedule_success(
        self,
        client,
        integration_db_session,
        schedule_create_payload,
        schedule_update_payload,
    ):
        """測試更新時段 - 成功。

        測試流程：
        request → CORS → Router → Schema → Service → CRUD → Model → DB → response。
        """
        # GIVEN：先建立一個時段，使用 fixture 提供的唯一資料
        create_response = client.post("/api/v1/schedules", json=schedule_create_payload)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_schedule = create_response.json()[0]
        schedule_id = created_schedule["id"]

        # 只更新備註，不更新時間，避免重疊檢查
        safe_update_data = {
            "schedule": {
                "note": "更新後的時段",
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

        # WHEN：呼叫更新時段 API
        response = client.patch(
            f"/api/v1/schedules/{schedule_id}", json=safe_update_data
        )

        # THEN：確認更新成功
        assert response.status_code == status.HTTP_200_OK
        data = response.json()  # 轉成 Python 物件
        assert "id" in data
        assert data["id"] == schedule_id

        # ===== 驗證回應資料結構 =====
        # 驗證更新後的資料
        assert data["note"] == "更新後的時段"
        assert data["updated_by"] == 1
        assert data["updated_by_role"] == "GIVER"
        # 驗證時間沒有改變
        assert data["start_time"] == created_schedule["start_time"]
        assert data["end_time"] == created_schedule["end_time"]
        # 驗證其他欄位保持不變
        assert data["giver_id"] == 1
        assert data["taker_id"] is None
        assert data["status"] == ScheduleStatusEnum.AVAILABLE.value
        assert data["date"] == "2024-12-25"
        assert data["created_by"] == 1
        assert data["created_by_role"] == "GIVER"

        # 時間戳記驗證
        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_at"] is not None
        assert data["updated_at"] is not None
        # 更新後，updated_at 應該不同於 created_at（或相同，取決於時間精度）

        # 軟刪除相關（更新時應仍為 null）
        assert data["deleted_at"] is None
        assert data["deleted_by"] is None
        assert data["deleted_by_role"] is None

        # ===== 查詢資料庫，驗證寫入的內容是否正確 =====

        # 從 API 回傳取得 id
        schedule_id = data["id"]

        # 查主鍵，故使用 get() 而不是 .query().filter(...).first()
        db_schedule = integration_db_session.get(ScheduleModel, schedule_id)

        # 驗證記錄存在
        assert db_schedule is not None

        # 驗證欄位值更新正確
        assert db_schedule.id == data["id"]
        assert db_schedule.giver_id == 1
        assert db_schedule.taker_id is None
        assert db_schedule.note == "更新後的時段"  # 驗證備註已更新
        assert db_schedule.created_by == 1
        assert db_schedule.created_by_role == "GIVER"
        assert db_schedule.updated_by == 1  # 驗證更新者
        assert db_schedule.updated_by_role == "GIVER"

        # ORM 將資料庫中 Enum 物件，轉回 Python 的 Enum 物件，故可以直接用 Enum 比對
        assert db_schedule.status == ScheduleStatusEnum.AVAILABLE

        # 驗證 ORM 資料型別轉換
        # 1. 請求階段，API 傳入的 date、time 是 JSON 字串格式
        # 2. Pydantic schema 將 JSON 字串，轉成 Python 的 date、time 物件
        # 3. ORM 將 Python 的 date、time 物件，寫入 MySQL/MariaDB 資料庫成 DATE、TIME 物件
        # 4. 查詢資料庫時，ORM 將資料庫中 DATE、TIME 物件，轉回 Python 的 date、time 物件
        assert db_schedule.date == date(2024, 12, 25)
        assert db_schedule.start_time == time(9, 0, 0)
        assert db_schedule.end_time == time(10, 0, 0)
        # 驗證 ORM 物件轉為字串後，與原始請求一致 (JSON 格式)
        assert str(db_schedule.date) == "2024-12-25"
        assert str(db_schedule.start_time) == "09:00:00"
        assert str(db_schedule.end_time) == "10:00:00"

        # 時間戳記驗證
        assert db_schedule.created_at is not None
        assert db_schedule.updated_at is not None
        # 更新後，created_at 應該保持不變，updated_at 應該被更新

        # 軟刪除相關（更新時應仍為 null）
        assert db_schedule.deleted_at is None
        assert db_schedule.deleted_by is None
        assert db_schedule.deleted_by_role is None

    def test_update_schedule_not_found(self, client, schedule_update_payload):
        """測試更新時段 - 時段不存在。"""
        # GIVEN：不存在的時段 ID 和有效的更新資料

        # WHEN：呼叫更新時段 API
        response = client.patch("/api/v1/schedules/99999", json=schedule_update_payload)

        # THEN：確認返回找不到錯誤
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert "時段不存在" in data["error"]["message"]

    def test_update_schedule_validation_error(self, client, schedule_create_payload):
        """測試更新時段 - 參數驗證錯誤。"""
        # GIVEN：先建立一個時段，使用 fixture 提供的唯一資料
        create_response = client.post("/api/v1/schedules", json=schedule_create_payload)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_schedule = create_response.json()[0]
        schedule_id = created_schedule["id"]

        # 無效的更新資料（時間邏輯錯誤）
        # 使用不會與現有時段重疊的時間來測試驗證邏輯
        invalid_data = {
            "schedule": {
                "start_time": "08:00:00",  # 早上時間，不會與下午時段重疊
                "end_time": "07:00:00",  # 結束時間早於開始時間
                "note": "無效時段",
            },
            "updated_by": 1,
            "updated_by_role": "GIVER",
        }

        # WHEN：呼叫更新時段 API
        response = client.patch(f"/api/v1/schedules/{schedule_id}", json=invalid_data)

        # THEN：確認返回驗證錯誤
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "error" in data

    # ===== 刪除時段 =====
    def test_delete_schedule_success(
        self,
        client,
        integration_db_session,
        schedule_create_payload,
        schedule_delete_payload,
    ):
        """測試刪除時段 - 成功。

        測試流程：
        request → CORS → Router → Schema → Service → CRUD → Model → DB → response。
        """
        # GIVEN：先建立一個時段，使用 fixture 提供的唯一資料
        create_response = client.post("/api/v1/schedules", json=schedule_create_payload)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_schedule = create_response.json()[0]
        schedule_id = created_schedule["id"]

        # WHEN：呼叫刪除時段 API
        response = client.request(
            "DELETE",
            f"/api/v1/schedules/{schedule_id}",
            content=json.dumps(schedule_delete_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
        )

        # THEN：確認刪除成功
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""

        # ===== 查詢資料庫，驗證軟刪除的內容是否正確 =====
        from datetime import date, time

        from app.models.schedule import Schedule as ScheduleModel

        # 查主鍵，故使用 get() 而不是 .query().filter(...).first()
        db_schedule = integration_db_session.get(ScheduleModel, schedule_id)

        # 驗證記錄存在（軟刪除不會真正刪除記錄）
        assert db_schedule is not None

        # 驗證基本欄位保持不變
        assert db_schedule.id == schedule_id
        assert db_schedule.giver_id == 1
        assert db_schedule.taker_id is None
        assert db_schedule.note == "測試時段"
        assert db_schedule.created_by == 1
        assert db_schedule.created_by_role == "GIVER"

        # ORM 將資料庫中 Enum 物件，轉回 Python 的 Enum 物件，故可以直接用 Enum 比對
        # 刪除時段時，狀態會自動改為 CANCELLED
        assert db_schedule.status == ScheduleStatusEnum.CANCELLED

        # 驗證 ORM 資料型別轉換
        # 1. 請求階段，API 傳入的 date、time 是 JSON 字串格式
        # 2. Pydantic schema 將 JSON 字串，轉成 Python 的 date、time 物件
        # 3. ORM 將 Python 的 date、time 物件，寫入 MySQL/MariaDB 資料庫成 DATE、TIME 物件
        # 4. 查詢資料庫時，ORM 將資料庫中 DATE、TIME 物件，轉回 Python 的 date、time 物件
        assert db_schedule.date == date(2024, 12, 25)
        assert db_schedule.start_time == time(9, 0, 0)
        assert db_schedule.end_time == time(10, 0, 0)
        # 驗證 ORM 物件轉為字串後，與原始請求一致 (JSON 格式)
        assert str(db_schedule.date) == "2024-12-25"
        assert str(db_schedule.start_time) == "09:00:00"
        assert str(db_schedule.end_time) == "10:00:00"

        # 時間戳記驗證
        assert db_schedule.created_at is not None
        assert db_schedule.updated_at is not None

        # 軟刪除相關（刪除後應設定）
        assert db_schedule.deleted_at is not None  # 刪除時間應該被設定
        assert db_schedule.deleted_by == 1  # 刪除者應為 1
        assert db_schedule.deleted_by_role == "GIVER"  # 刪除者角色應為 GIVER

        # 驗證 is_deleted 屬性
        assert db_schedule.is_deleted is True
        assert db_schedule.is_active is False

    def test_delete_schedule_not_found(self, client, schedule_delete_payload):
        """測試刪除時段 - 時段不存在。"""
        # GIVEN：不存在的時段 ID 和有效的刪除資料

        # WHEN：呼叫刪除時段 API
        response = client.request(
            "DELETE",
            "/api/v1/schedules/99999",
            content=json.dumps(schedule_delete_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
        )

        # THEN：確認返回找不到錯誤
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert "時段不存在" in data["error"]["message"]

    def test_delete_schedule_validation_error(self, client):
        """測試刪除時段 - 參數驗證錯誤。"""
        # GIVEN：無效的刪除資料（缺少必要欄位）
        invalid_data = {
            # 缺少必要欄位
        }

        # WHEN：呼叫刪除時段 API
        response = client.request(
            "DELETE",
            "/api/v1/schedules/1",
            content=json.dumps(invalid_data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
        )

        # THEN：確認返回驗證錯誤
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_schedule_routes_http_methods(self, client):
        """測試時段路由 - HTTP 方法限制。"""
        # GIVEN：時段路由端點

        # WHEN：使用不支援的 HTTP 方法
        get_response = client.get("/api/v1/schedules/1")  # 支援
        post_response = client.post("/api/v1/schedules/1")  # 不支援
        put_response = client.put("/api/v1/schedules/1")  # 不支援

        # THEN：確認方法支援正確
        assert get_response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]
        assert post_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert put_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_schedule_routes_content_type(self, client):
        """測試時段路由 - 內容類型。"""
        # GIVEN：時段路由端點

        # WHEN：呼叫 API 端點
        response = client.get("/api/v1/schedules")

        # THEN：確認內容類型正確
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/json"
