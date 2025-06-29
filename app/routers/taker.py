# app/routers/taker.py
from fastapi import APIRouter
import logging

# 設定日誌
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/taker", tags=["taker"])

@router.get("/{taker_id}")
def get_taker_profile(taker_id: int):
    logger.info(f"get_taker_profile() called: taker_id={taker_id}")
    logger.info("get_taker_profile() completed: 返回 Taker 個人資料")
    pass

@router.post("/")
def create_or_update_taker(data: dict):
    logger.info(f"create_or_update_taker() called: data={data}")
    logger.info("create_or_update_taker() completed: Taker 資料已建立或更新")
    pass
