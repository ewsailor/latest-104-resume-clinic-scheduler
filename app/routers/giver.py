# app/routers/giver.py
from fastapi import APIRouter
import logging

# 設定日誌
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/giver", tags=["giver"])

@router.get("/{giver_id}")
def get_giver_profile(giver_id: int):
    logger.info(f"get_giver_profile() called: giver_id={giver_id}")
    logger.info("get_giver_profile() completed: 返回 Giver 個人資料")
    pass

@router.post("/")
def create_or_update_giver(data: dict):
    logger.info(f"create_or_update_giver() called: data={data}")
    logger.info("create_or_update_giver() completed: Giver 資料已建立或更新")
    pass
