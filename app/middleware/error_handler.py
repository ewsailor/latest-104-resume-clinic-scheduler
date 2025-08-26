"""
簡化的錯誤處理中間件。

提供統一的錯誤處理機制，適合投履歷展示。
"""

# ===== 標準函式庫 =====
import logging

# ===== 第三方套件 =====
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# ===== 本地模組 =====
from app.errors import format_error_response

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """錯誤處理中間件"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """處理請求並捕獲錯誤"""
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self._handle_exception(request, exc)

    async def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """處理異常並返回標準化的錯誤回應"""

        error_response = format_error_response(exc)

        # 從格式化結果中取得狀態碼
        status_code = error_response["error"]["status_code"]

        logger.error(f"錯誤: {request.method} {request.url.path} - {str(exc)}")

        return JSONResponse(status_code=status_code, content=error_response)


def setup_error_handlers(app):
    """設定錯誤處理器"""
    app.add_middleware(ErrorHandlerMiddleware)
    logger.info("錯誤處理器設定完成")
