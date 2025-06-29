# app/routers/chat.py
from fastapi import APIRouter
import logging

# 設定日誌
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/{giver_id}/{taker_id}")
def get_chat(giver_id: int, taker_id: int):
    logger.info(f"get_chat() called: giver_id={giver_id}, taker_id={taker_id}")
    logger.info("get_chat() completed: 返回聊天記錄")
    pass

@router.post("/{giver_id}/{taker_id}")
def post_message(giver_id: int, taker_id: int, message: dict):
    logger.info(f"post_message() called: giver_id={giver_id}, taker_id={taker_id}, message={message}")
    logger.info("post_message() completed: 訊息已發布")
    pass
