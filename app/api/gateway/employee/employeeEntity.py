import httpx

from app.core.apiUrl import API_BASE_URL


async def fetch_master(endpoint: str, params: dict = None, headers: dict = None):
    url = f"{API_BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


async def fetch_employee(params: dict, headers: dict):
    data = await fetch_master("/employee/newEmployee", params, headers)
    if isinstance(data, list):
        return {"new_employees": data}
    return data


async def fetch_offboarding(params: dict, headers: dict):
    data = await fetch_master("/employee/offboarding", params, headers)
    if isinstance(data, list):
        return {"offboarding": data}
    return data
