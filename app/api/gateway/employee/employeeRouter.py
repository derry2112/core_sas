from fastapi import APIRouter, Header
from app.api.gateway.employee.employeeService import (
    get_employee_service,
    get_offboarding_service,
)


router = APIRouter()


@router.get("/newEmployee", response_model=dict)
async def get_employee_endpoint(
    limit: int = 10, skip: int = 0, x_api_key: str = Header(...)
):
    return await get_employee_service(limit, skip, x_api_key)


@router.get("/offboarding", response_model=dict)
async def get_offboarding_endpoint(
    limit: int = 10, skip: int = 0, x_api_key: str = Header(...)
):
    return await get_offboarding_service(limit, skip, x_api_key)
