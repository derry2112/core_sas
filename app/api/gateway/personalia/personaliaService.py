from fastapi import HTTPException

from app.api.gateway.personalia.personaliaEntity import (
    fetch_birthday,
    fetch_emergency,
    fetch_employee,
    fetch_offboarding,
    fetch_profile,
    is_valid_email,
)
from app.core.logging import logger


# PROFILE
async def get_profile_service(email: str):
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    params = {"email": email}
    try:
        response = await fetch_profile(params=params)
        if response.get("code") != 200:
            logger.error(f"Failed to fetch profile: {response.get('message')}")
            raise HTTPException(status_code=400, detail=response.get("message"))
        return response
    except HTTPException as e:
        logger.error(f"HTTPException: {str(e)}")
        raise e
    except Exception as e:
        logger.exception("Unexpected error in get_profile_service")
        raise HTTPException(status_code=500, detail=str(e))


# BIRTHDAY
async def get_birthday_service(page: int, limit: int):
    params = {"page": page, "limit": limit}
    return await fetch_birthday(params=params)


# OFFBOARDING
async def get_offboarding_service(page: int, limit: int):
    params = {"page": page, "limit": limit}
    return await fetch_offboarding(params=params)


# EMPLOYEE
async def get_employee_service(page: int, limit: int):
    params = {"page": page, "limit": limit}
    return await fetch_employee(params=params)


# EMERGENCY
async def get_emergency_service(email: str):
    params = {"email": email}
    return await fetch_emergency(params=params)
