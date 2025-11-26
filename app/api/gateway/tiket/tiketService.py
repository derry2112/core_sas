import json

from fastapi import HTTPException, Response

from app.api.gateway.tiket.tiketEntity import fetch_all_ticket_pics
from app.core.logging import logger


async def get_all_ticket_pics_gateway_service(
    search: str, skip: int, limit: int, order_by: str, headers: dict
) -> Response:
    params = {"search": search, "skip": skip, "limit": limit, "order_by": order_by}

    try:
        data = await fetch_all_ticket_pics(params=params, headers=headers)
        return Response(content=json.dumps(data), media_type="application/json")
    except HTTPException as e:
        logger.error(f"[Tiketing] Error fetching PICs: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"[Tiketing] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
