import json

import httpx
from fastapi import HTTPException

from app.core.apiUrl import API_BASE_URL
from app.core.logging import logger


async def fetch_data(endpoint: str, params: dict = None, headers: dict = None):
    url = f"{API_BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                logger.error(f"Expected JSON but got: {content_type}")
                raise HTTPException(
                    status_code=500, detail="Unexpected response format, not JSON"
                )

            lines = response.text.splitlines()
            json_data = []
            for line in lines:
                try:
                    json_data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON in line: {e}")
                    continue

            return json_data

        except httpx.RequestError as e:
            logger.error("Request error fetching %s: %s", url, e)
            raise HTTPException(status_code=500, detail="Request failed")

        except Exception as e:
            logger.error("Unexpected error during request to %s: %s", url, e)
            raise HTTPException(status_code=500, detail="Unknown error")


async def fetch_absen_tgl(params: dict, headers: dict):
    return await fetch_data("/absensi/byDate_Location", params, headers)
