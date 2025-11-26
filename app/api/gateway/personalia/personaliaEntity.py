import httpx
from fastapi import HTTPException

from app.core.apiUrl import PERSONALIA_BASE_URL
from app.core.logging import logger


def is_valid_email(email: str) -> bool:
    import re

    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


async def fetch_data(endpoint: str, params: dict = None, headers: dict = None):
    url = f"{PERSONALIA_BASE_URL}{endpoint}"
    logger.info(f"Requesting {url} with params={params}, headers={headers}")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error(
            "Upstream API error %s: %s", e.response.status_code, e.response.text
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Upstream error: {e.response.text}",
        )

    except httpx.RequestError as e:
        logger.error("Request to %s failed: %s", url, str(e))
        raise HTTPException(status_code=502, detail="Failed to reach upstream API")

    except Exception:
        logger.exception("Unexpected error calling %s", url)
        raise HTTPException(status_code=500, detail="Internal server error")


async def fetch_profile(params: dict):
    return await fetch_data("/api/sas/profile", params)


async def fetch_birthday(params: dict):
    return await fetch_data("/api/sas/dashboard/personalia/birthday", params)


async def fetch_offboarding(params: dict):
    return await fetch_data("/api/sas/dashboard/personalia/count/offboarding", params)


async def fetch_employee(params: dict):
    return await fetch_data("/api/sas/dashboard/personalia/employee", params)


async def fetch_emergency(params: dict):
    return await fetch_data(
        "/api/sas/dashboard/personalia/kontak-darurat/by-email", params
    )
