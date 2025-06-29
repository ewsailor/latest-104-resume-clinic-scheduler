# app/routers/match.py
from fastapi import APIRouter
import logging

# 設定日誌
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/match", tags=["match"])

@router.get("/success")
def get_all_matches():
    logger.info("get_all_matches() called: 取得所有配對")
    logger.info("get_all_matches() completed: 返回所有配對資料")
    pass

@router.post("/")
def create_match(giver_id: int, taker_id: int):
    logger.info(f"create_match() called: giver_id={giver_id}, taker_id={taker_id}")
    logger.info("create_match() completed: 配對已建立")
    pass
