"""
全域錯誤處理中間件。

提供統一的錯誤處理機制，捕獲所有未處理的異常並返回標準化的錯誤回應。
"""

import logging
import traceback
import uuid
from typing import Any

from fastapi import Request, Response, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.settings import settings
from app.errors import (
    APIError,
    ErrorCode,
    format_error_response,
)
from app.utils.timezone import get_utc_timestamp

# 設定 logger
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """全域錯誤處理中間件"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        處理請求並捕獲錯誤。

        Args:
            request: FastAPI 請求物件
            call_next: 下一個中間件或路由處理器

        Returns:
            Response: HTTP 回應
        """
        # 生成請求 ID 用於追蹤
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 記錄請求開始 - 根據配置決定是否記錄
        if request.url.path.startswith("/api/"):
            if settings.log_api_requests:
                logger.info(
                    f"API 請求開始: {request.method} {request.url.path} [ID: {request_id}]"
                )
        else:
            if settings.log_static_requests:
                logger.debug(
                    f"靜態資源請求: {request.method} {request.url.path} [ID: {request_id}]"
                )

        try:
            # 執行下一個中間件或路由處理器
            response = await call_next(request)

            # 記錄請求成功 - 根據配置決定是否記錄
            if request.url.path.startswith("/api/"):
                if settings.log_api_requests:
                    logger.info(
                        f"API 請求成功: {request.method} {request.url.path} [ID: {request_id}] - {response.status_code}"
                    )
            else:
                if settings.log_static_requests:
                    logger.debug(
                        f"靜態資源請求成功: {request.method} {request.url.path} [ID: {request_id}] - {response.status_code}"
                    )

            return response

        except Exception as exc:
            # 記錄請求失敗
            logger.error(
                f"請求失敗: {request.method} {request.url.path} [ID: {request_id}]"
            )

            # 處理不同類型的錯誤
            return await self._handle_exception(request, exc, request_id)

    async def _handle_exception(
        self, request: Request, exc: Exception, request_id: str
    ) -> JSONResponse:
        """
        處理異常並返回標準化的錯誤回應。

        Args:
            request: FastAPI 請求物件
            exc: 異常物件
            request_id: 請求 ID

        Returns:
            JSONResponse: 標準化的錯誤回應
        """
        # 準備請求資訊用於日誌記錄
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "path_params": dict(request.path_params),
            "request_id": request_id,
        }

        # 根據異常類型處理
        if isinstance(exc, APIError):
            # 處理自定義 API 錯誤
            error_response = format_error_response(exc)
            status_code = exc.status_code

        elif isinstance(exc, HTTPException):
            # 處理 FastAPI HTTPException
            error_response = format_error_response(exc)
            status_code = exc.status_code

        elif isinstance(exc, StarletteHTTPException):
            # 處理 Starlette HTTPException
            error_response = format_error_response(exc)
            status_code = exc.status_code

        elif isinstance(exc, RequestValidationError):
            # 處理請求驗證錯誤
            error_response = {
                "error": {
                    "code": ErrorCode.VALIDATION_ERROR,
                    "message": "請求資料驗證失敗",
                    "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "timestamp": get_utc_timestamp(),
                    "details": exc.errors(),
                }
            }
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        else:
            # 處理未預期的錯誤
            error_response = {
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR,
                    "message": "內部伺服器錯誤",
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "timestamp": get_utc_timestamp(),
                }
            }
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            # 在開發環境包含詳細錯誤資訊
            if settings.debug:
                error_response["error"]["details"] = {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                }

        # 記錄錯誤
        logger.error(f"中間件錯誤: {str(exc)}", exc_info=True)

        # 返回標準化的錯誤回應
        return JSONResponse(status_code=status_code, content=error_response)


def create_error_handler_middleware(app) -> ErrorHandlerMiddleware:
    """
    創建錯誤處理中間件實例。

    Args:
        app: FastAPI 應用程式實例

    Returns:
        ErrorHandlerMiddleware: 錯誤處理中間件實例
    """
    return ErrorHandlerMiddleware(app)


# 全域異常處理器（用於 FastAPI 的 exception_handler 裝飾器）
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTPException 處理器。

    Args:
        request: FastAPI 請求物件
        exc: HTTPException 實例

    Returns:
        JSONResponse: 標準化的錯誤回應
    """
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))

    error_response = format_error_response(exc)

    # 記錄錯誤
    logger.error(f"HTTPException: {str(exc)}", exc_info=True)

    return JSONResponse(status_code=exc.status_code, content=error_response)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    請求驗證錯誤處理器。

    Args:
        request: FastAPI 請求物件
        exc: RequestValidationError 實例

    Returns:
        JSONResponse: 標準化的錯誤回應
    """
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))

    error_response = {
        "error": {
            "code": ErrorCode.VALIDATION_ERROR,
            "message": "請求資料驗證失敗",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "timestamp": get_utc_timestamp(),
            "details": exc.errors(),
        }
    }

    # 記錄錯誤
    logger.error(f"ValidationError: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用異常處理器。

    Args:
        request: FastAPI 請求物件
        exc: 異常實例

    Returns:
        JSONResponse: 標準化的錯誤回應
    """
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))

    error_response = {
        "error": {
            "code": ErrorCode.INTERNAL_ERROR,
            "message": "內部伺服器錯誤",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "timestamp": get_utc_timestamp(),
        }
    }

    # 在開發環境包含詳細錯誤資訊
    if settings.debug:
        error_response["error"]["details"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }

    # 記錄錯誤
    logger.error(f"GeneralException: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response
    )


def setup_error_handlers(app):
    """
    設定 FastAPI 應用程式的錯誤處理器。

    Args:
        app: FastAPI 應用程式實例
    """
    # 註冊異常處理器
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # 添加錯誤處理中間件
    app.add_middleware(ErrorHandlerMiddleware)

    logger.info("錯誤處理器設定完成")
