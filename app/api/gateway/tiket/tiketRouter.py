from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query

from app.api.gateway.tiket.tiketService import get_all_ticket_pics_gateway_service
from app.api.users.userAuth import verify_clerk_token_header

router = APIRouter()


@router.get("/get-all-tickets")
async def get_all_pic_gateway_router(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    order_by: Literal["asc", "desc"] = Query("asc"),
    user_email: str = Depends(verify_clerk_token_header),
):
    return await get_all_ticket_pics_gateway_service(
        search=search, skip=skip, limit=limit, order_by=order_by, user_email=user_email
    )
