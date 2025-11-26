from fastapi import APIRouter, Header, HTTPException

from app.api.gateway.notification.notifService import get_notif_service

router = APIRouter()


@router.get("/notif", response_model=dict)
async def get_notif_endpoint(
    penempatan: str, limit: int = 10, skip: int = 0, x_api_key: str = Header(...)
):
    try:
        return await get_notif_service(penempatan, limit, skip, x_api_key)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
