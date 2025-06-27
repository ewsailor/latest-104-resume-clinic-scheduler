# app/routers/match.py
from fastapi import APIRouter

router = APIRouter(prefix="/match", tags=["match"])

@router.get("/success")
def get_all_matches():
    pass

@router.post("/")
def create_match(giver_id: int, taker_id: int):
    pass
