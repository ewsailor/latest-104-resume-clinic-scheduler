"""
Giver 管理 API 路由模組。

提供 Giver 相關的 API 端點，包括查詢 Giver 列表和詳細資訊。
"""

from typing import Any, Dict, Optional  # 型別提示

# ===== 第三方套件 =====
from fastapi import APIRouter, HTTPException, Query, status  # 路由和錯誤處理

# ===== 本地模組 =====
from app.data.givers import (
    get_all_givers,
    get_all_industries,
    get_all_topics,
    get_giver_by_id,
    get_givers_by_industry,
    get_givers_by_topic,
    get_givers_count,
)

# 建立路由器
router = APIRouter(prefix="/api", tags=["Givers"])


@router.get("/givers")
async def get_givers(
    topic: Optional[str] = Query(None, description="根據服務項目篩選"),
    industry: Optional[str] = Query(None, description="根據產業篩選"),
    page: int = Query(1, ge=1, description="頁碼"),
    per_page: int = Query(12, ge=1, le=100, description="每頁數量"),
) -> Dict[str, Any]:
    """
    取得 Giver 列表。

    Args:
        topic: 可選的服務項目篩選條件
        industry: 可選的產業篩選條件
        page: 頁碼（從 1 開始）
        per_page: 每頁數量

    Returns:
        dict: 包含 Giver 列表和分頁資訊的回應
    """
    try:
        # 取得所有 Giver 資料
        givers = get_all_givers()

        # 根據條件篩選
        if topic:
            givers = get_givers_by_topic(topic)

        if industry:
            # 如果已經有 topic 篩選，則在結果中再篩選 industry
            if topic:
                givers = [
                    giver for giver in givers if giver.get("industry") == industry
                ]
            else:
                givers = get_givers_by_industry(industry)

        # 計算分頁
        total = len(givers)
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_givers = givers[start_index:end_index]

        return {
            "results": paginated_givers,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得 Giver 列表失敗: {str(e)}",
        )


@router.get("/givers/topics")
async def get_topics() -> Dict[str, Any]:
    """
    取得所有可用的服務項目列表。

    Returns:
        dict: 包含所有可用服務項目的回應
    """
    try:
        topics = get_all_topics()
        return {
            "results": topics,
            "total": len(topics),
            "description": "所有可用的服務項目列表",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得服務項目列表失敗: {str(e)}",
        )


@router.get("/givers/topics/{topic}")
async def get_givers_by_topic_endpoint(topic: str) -> Dict[str, Any]:
    """
    根據服務項目取得 Giver 列表。

    Args:
        topic: 服務項目名稱

    Returns:
        dict: 符合條件的 Giver 列表
    """
    try:
        givers = get_givers_by_topic(topic)
        return {"results": givers, "total": len(givers), "topic": topic}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"根據服務項目篩選 Giver 失敗: {str(e)}",
        )


@router.get("/givers/industries")
async def get_industries() -> Dict[str, Any]:
    """
    取得所有可用的產業列表。

    Returns:
        dict: 包含所有可用產業的回應
    """
    try:
        industries = get_all_industries()
        return {
            "results": industries,
            "total": len(industries),
            "description": "所有可用的產業列表",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得產業列表失敗: {str(e)}",
        )


@router.get("/givers/industries/{industry}")
async def get_givers_by_industry_endpoint(industry: str) -> Dict[str, Any]:
    """
    根據產業取得 Giver 列表。

    Args:
        industry: 產業名稱

    Returns:
        dict: 符合條件的 Giver 列表
    """
    try:
        givers = get_givers_by_industry(industry)
        return {"results": givers, "total": len(givers), "industry": industry}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"根據產業篩選 Giver 失敗: {str(e)}",
        )


@router.get("/givers/stats/count")
async def get_givers_count_endpoint() -> Dict[str, int]:
    """
    取得 Giver 總數統計。

    Returns:
        dict: 包含 Giver 總數的回應
    """
    try:
        count = get_givers_count()
        return {"count": count}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得 Giver 統計失敗: {str(e)}",
        )


@router.get("/givers/{giver_id}")
async def get_giver(giver_id: int) -> Dict[str, Any]:
    """
    根據 ID 取得特定 Giver 資料。

    Args:
        giver_id: Giver ID

    Returns:
        dict: Giver 詳細資料

    Raises:
        HTTPException: 當 Giver 不存在時拋出 404 錯誤
    """
    try:
        giver = get_giver_by_id(giver_id)
        if not giver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到 ID 為 {giver_id} 的 Giver",
            )
        return giver

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得 Giver 資料失敗: {str(e)}",
        )
