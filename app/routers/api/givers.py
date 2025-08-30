"""Giver 管理 API 路由模組。

提供 Giver 相關的 API 端點，包括查詢 Giver 列表和詳細資訊。
"""

# ===== 標準函式庫 =====
from typing import Any

# ===== 第三方套件 =====
from fastapi import APIRouter, HTTPException, Query, status

# ===== 本地模組 =====
from app.data.givers import (
    get_all_givers,
    get_giver_by_id,
)
from app.decorators import handle_api_errors_async

# 建立路由器
router = APIRouter(prefix="/api/v1", tags=["Givers"])


@router.get("/givers")
@handle_api_errors_async()
async def get_givers(
    page: int = Query(1, ge=1, description="頁碼"),
    per_page: int = Query(12, ge=1, le=100, description="每頁數量"),
) -> dict[str, Any]:
    """取得 Giver 列表。"""
    # 取得所有 Giver 資料
    givers = get_all_givers()

    # 計算分頁
    total = len(givers)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_givers = givers[start_index:end_index]

    result = {
        "results": paginated_givers,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }

    return result


@router.get("/givers/{giver_id}")
@handle_api_errors_async()
async def get_giver(giver_id: int) -> dict[str, Any]:
    """根據 ID 取得特定 Giver 資料。"""
    result = get_giver_by_id(giver_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到 ID 為 {giver_id} 的 Giver",
        )
    return result
