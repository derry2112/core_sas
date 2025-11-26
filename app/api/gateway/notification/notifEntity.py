import re

import httpx

from app.core.apiUrl import API_BASE_URL


def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


async def fetch_master(endpoint: str, params: dict = None, headers: dict = None):
    url = f"{API_BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


async def fetch_notif(params: dict, headers: dict):
    return await fetch_master("/notification/notif", params, headers)
