from fastapi import APIRouter, Depends

from app.api.gateway.personalia.personaliaService import (
    get_birthday_service,
    get_emergency_service,
    get_employee_service,
    get_offboarding_service,
    get_profile_service,
)
from app.api.users.userAuth import verify_clerk_token_header

router = APIRouter()


@router.get("/profile", response_model=dict)
async def get_profile(user_email: str = Depends(verify_clerk_token_header)):
    return await get_profile_service(email=user_email)


@router.get("/birthday", response_model=dict)
async def get_birthday_endpoint(
    page: int = 1,
    perPage: int = 10,
    user_email: str = Depends(verify_clerk_token_header),
):
    return await get_birthday_service(page, perPage)


@router.get("/offboarding", response_model=dict)
async def get_offboarding_endpoint(
    page: int = 1,
    perPage: int = 10,
    user_email: str = Depends(verify_clerk_token_header),
):
    return await get_offboarding_service(page, perPage)


@router.get("/employee", response_model=dict)
async def get_employee_endpoint(
    page: int = 1,
    perPage: int = 25,
    user_email: str = Depends(verify_clerk_token_header),
):
    return await get_employee_service(page, perPage)


@router.get("/emergency", response_model=dict)
async def get_emergency_endpoint(user_email: str = Depends(verify_clerk_token_header)):
    return await get_emergency_service(email=user_email)
