# app/routers/admin.py
from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/overview")
def admin_dashboard():
    pass
