import httpx

from app.core.apiUrl import API_BASE_URL


async def fetch_master(endpoint: str, params: dict = None, headers: dict = None):
    url = f"{API_BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


async def fetch_dasata(params: dict, headers: dict):
    return await fetch_master("/dasata/pembayaran", params, headers)
