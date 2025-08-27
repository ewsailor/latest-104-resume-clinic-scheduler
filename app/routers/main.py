"""主要路由模組。

包含首頁、健康檢查等基礎路由。
"""

# ===== 第三方套件 =====
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# ===== 本地模組 =====
from app.decorators import log_operation

router = APIRouter()


@router.get(
    "/",
    response_class=HTMLResponse,
    tags=["Pages"],
)
@log_operation("首頁訪問")
async def read_index(request: Request) -> HTMLResponse:
    """首頁路由 - 顯示履歷診療室主頁面。

    Args: request: FastAPI 請求物件。

    Returns: HTMLResponse: 渲染後的 HTML 頁面。
    """
    templates: Jinja2Templates = request.app.state.templates
    result = templates.TemplateResponse(request, "index.html")

    return result
