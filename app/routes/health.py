from fastapi import APIRouter

router = APIRouter()

@router.get("/check-status")
def checkStatus():
    return {"ok": True, "status": "online", "service": "chat"}

@router.get("/api/ping")
def pong():
    return {"ok": True, "message": "pong"}
