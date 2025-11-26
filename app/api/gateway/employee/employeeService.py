from fastapi import HTTPException

from app.api.gateway.employee.employeeEntity import fetch_employee, fetch_offboarding
from app.core.apiUrl import EMPLOYEE_API_KEY


async def get_employee_service(limit: int, skip: int, x_api_key: str):
    if x_api_key != EMPLOYEE_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API key")

    params = {"limit": limit, "skip": skip}
    headers = {"x-api-key": x_api_key}

    try:
        return await fetch_employee(params=params, headers=headers)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_offboarding_service(limit: int, skip: int, x_api_key: str):
    if x_api_key != EMPLOYEE_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API key")

    params = {"limit": limit, "skip": skip}
    headers = {"x-api-key": x_api_key}

    try:
        return await fetch_offboarding(params=params, headers=headers)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
