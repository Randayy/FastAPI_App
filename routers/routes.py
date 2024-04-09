from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health_check():
    return { 
            "status_code": 200,
            "detail": "ok",
            "result": "working"
            }