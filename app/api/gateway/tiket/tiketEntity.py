from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException

from app.core.apiUrl import TIKETING_BASE_URL
from app.core.logging import logger


async def fetch_data_tiketing(
    endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None
) -> Any:
    url = f"{TIKETING_BASE_URL}{endpoint}"

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                logger.error(f"[Tiketing] Expected JSON but got: {content_type}")
                raise HTTPException(
                    status_code=500,
                    detail="Unexpected response format from Tiketing service",
                )

            return response.json()

        except httpx.RequestError as e:
            logger.error(f"[Tiketing] Request error to {url}: {e}")
            raise HTTPException(status_code=500, detail="Request to Tiketing failed")

        except Exception as e:
            logger.error(f"[Tiketing] Unexpected error calling {url}: {e}")
            raise HTTPException(
                status_code=500, detail="Internal error contacting Tiketing service"
            )


async def fetch_all_ticket_pics(params: Dict[str, Any], headers: Dict[str, str]) -> Any:
    return await fetch_data_tiketing(
        "/ticket/get-all-pic/", params=params, headers=headers
    )
