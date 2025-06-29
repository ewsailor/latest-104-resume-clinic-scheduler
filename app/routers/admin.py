# app/routers/admin.py
from fastapi import APIRouter
import logging

# 設定日誌
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/overview")
def admin_dashboard():
    logger.info("admin_dashboard() called: 管理員儀表板")
    logger.info("admin_dashboard() completed: 返回管理員儀表板")
    pass
