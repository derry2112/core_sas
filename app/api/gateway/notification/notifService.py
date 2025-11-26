from fastapi import HTTPException

from app.api.gateway.notification.notifEntity import fetch_notif
from app.core.apiUrl import NOTIF_API_KEY


async def get_notif_service(penempatan: str, limit: int, skip: int, x_api_key: str):
    if x_api_key != NOTIF_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API key")

    params = {"penempatan": penempatan, "limit": limit, "skip": skip}
    headers = {"x-api-key": x_api_key}

    try:
        response = await fetch_notif(params=params, headers=headers)
        if not response or "data" not in response or not response["data"]:
            return {"message": "Data not found"}
        return response
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Notification failed")
