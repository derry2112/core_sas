from fastapi import APIRouter, Depends
from typing import Annotated
from app.api.gateway.direct.directEntity import penaburs, best
from app.services.jwtMiddleware import require_auth

router = APIRouter()


@router.post("/best/", response_model=None)
async def best_endpoint(user_data: Annotated[dict, Depends(require_auth)]):
    data = await best(user_data)
    return {
        "message": "Email forwarded successfully",
        "data": data,
    }


@router.post("/penaburs/", response_model=None)
async def penaburs_endpoint(user_data: Annotated[dict, Depends(require_auth)]):
    data = await penaburs(user_data)
    return {
        "message": "Email forwarded successfully",
        "data": data,
    }
