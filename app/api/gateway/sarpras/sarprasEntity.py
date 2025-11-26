import httpx

from app.core.apiUrl import RUANGAN_BASE_URL, SARPRAS_BASE_URL


async def fetch_data_kendaraan(endpoint: str, params: dict = None):
    url = f"{SARPRAS_BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_data_ruangan(endpoint: str, params: dict = None):
    url = f"{RUANGAN_BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_ruangan(params: dict):
    return await fetch_data_ruangan("/api/peminjaman-ruangan", params)


async def fetch_kendaraan(params: dict):
    return await fetch_data_kendaraan("/api/peminjaman-kendaraan", params)
