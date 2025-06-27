# app/routers/chat.py
from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/{giver_id}/{taker_id}")
def get_chat(giver_id: int, taker_id: int):
    pass

@router.post("/{giver_id}/{taker_id}")
def post_message(giver_id: int, taker_id: int, message: dict):
    pass
