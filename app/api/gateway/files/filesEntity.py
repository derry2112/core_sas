import re

import httpx

from app.core.apiUrl import API_BASE_URL


def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


async def fetch_master_files(endpoint: str, params: dict = None):
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    url = f"{API_BASE_URL.rstrip('/')}{endpoint}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_files(params: dict):
    return await fetch_master_files("/files/", params)
