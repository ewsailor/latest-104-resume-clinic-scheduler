# app/routers/giver.py
from fastapi import APIRouter

router = APIRouter(prefix="/giver", tags=["giver"])

@router.get("/{giver_id}")
def get_giver_profile(giver_id: int):
    pass

@router.post("/")
def create_or_update_giver(data: dict):
    pass
