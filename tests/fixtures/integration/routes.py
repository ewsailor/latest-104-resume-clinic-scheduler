"""整合測試路由 fixtures。

提供整合測試所需的路由相關 fixtures 和測試資料。
"""

# ===== 標準函式庫 =====

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====


@pytest.fixture
def sample_schedule_create_data():
    """建立範例時段建立資料。"""
    return {
        "schedules": [
            {
                "giver_id": 1,
                "date": "2024-01-15",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "note": "測試時段 1",
            },
            {
                "giver_id": 1,
                "date": "2024-01-16",
                "start_time": "14:00:00",
                "end_time": "15:00:00",
                "note": "測試時段 2",
            },
        ],
        "created_by": 1,
        "created_by_role": "GIVER",
    }


@pytest.fixture
def sample_schedule_update_data():
    """建立範例時段更新資料。"""
    return {
        "schedule": {
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "note": "更新後的時段",
        },
        "updated_by": 1,
        "updated_by_role": "GIVER",
    }


@pytest.fixture
def sample_schedule_delete_data():
    """建立範例時段刪除資料。"""
    return {"deleted_by": 1, "deleted_by_role": "GIVER"}


@pytest.fixture
def invalid_schedule_data():
    """建立無效的時段資料。"""
    return {
        "schedules": [
            {
                "giver_id": 1,
                # 缺少 date 欄位
                "start_time": "09:00:00",
                "end_time": "10:00:00",
            }
        ],
        "created_by": 1,
        "created_by_role": "GIVER",
    }


@pytest.fixture
def time_logic_error_data():
    """建立時間邏輯錯誤的時段資料。"""
    return {
        "schedules": [
            {
                "giver_id": 1,
                "date": "2024-01-15",
                "start_time": "10:00:00",
                "end_time": "09:00:00",  # 結束時間早於開始時間
                "note": "無效時段",
            }
        ],
        "created_by": 1,
        "created_by_role": "GIVER",
    }


@pytest.fixture
def sample_query_params():
    """建立範例查詢參數。"""
    return {"giver_id": 1, "taker_id": 2, "status_filter": "AVAILABLE"}


@pytest.fixture
def invalid_query_params():
    """建立無效的查詢參數。"""
    return {
        "giver_id": 0,  # 必須大於 0
        "taker_id": -1,  # 必須大於 0
        "status_filter": "INVALID_STATUS",
    }


@pytest.fixture
def sample_schedule_responses():
    """建立範例時段回應資料。"""
    return [
        {
            "id": 1,
            "giver_id": 1,
            "taker_id": None,
            "date": "2024-01-15",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "status": "AVAILABLE",
            "note": "可預約時段",
            "created_at": "2024-01-01T00:00:00Z",
            "created_by": 1,
            "created_by_role": "GIVER",
            "updated_at": "2024-01-01T00:00:00Z",
            "updated_by": 1,
            "updated_by_role": "GIVER",
            "deleted_at": None,
            "deleted_by": None,
            "deleted_by_role": None,
        },
        {
            "id": 2,
            "giver_id": 1,
            "taker_id": 2,
            "date": "2024-01-16",
            "start_time": "14:00:00",
            "end_time": "15:00:00",
            "status": "PENDING",
            "note": "待確認時段",
            "created_at": "2024-01-01T00:00:00Z",
            "created_by": 2,
            "created_by_role": "TAKER",
            "updated_at": "2024-01-01T00:00:00Z",
            "updated_by": 2,
            "updated_by_role": "TAKER",
            "deleted_at": None,
            "deleted_by": None,
            "deleted_by_role": None,
        },
    ]


@pytest.fixture
def sample_error_responses():
    """建立範例錯誤回應資料。"""
    return {
        "validation_error": {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["body", "schedules", 0, "date"],
                    "msg": "Field required",
                    "input": None,
                    "ctx": {"error": "missing"},
                }
            ]
        },
        "business_logic_error": {
            "error": {
                "message": "開始時間必須早於結束時間",
                "status_code": 400,
                "code": "ROUTER_BAD_REQUEST",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {},
            }
        },
        "not_found_error": {
            "error": {
                "message": "時段不存在: ID=99999",
                "status_code": 404,
                "code": "SERVICE_SCHEDULE_NOT_FOUND",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {},
            }
        },
    }


@pytest.fixture
def sample_http_headers():
    """建立範例 HTTP 標頭。"""
    return {
        "content_type": "application/json",
        "accept": "application/json",
        "user_agent": "test-client/1.0",
        "authorization": "Bearer test-token",
    }


@pytest.fixture
def sample_html_content():
    """建立範例 HTML 內容。"""
    return """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>履歷診療室</title>
    </head>
    <body>
        <h1>履歷診療室</h1>
        <div class="giver-list">
            <div class="giver-item">
                <h2>測試 Giver</h2>
                <p>專業領域：軟體開發</p>
            </div>
        </div>
    </body>
    </html>
    """
