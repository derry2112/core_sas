from fastapi import HTTPException

from app.api.gateway.dasata.dasataEntity import fetch_dasata
from app.core.apiUrl import DASATA_API_KEY
from app.core.logging import logger


async def get_dasata_service(
    penempatan: str, kls: str, status: str, limit: int, skip: int, x_api_key: str
):
    if x_api_key != DASATA_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API key")

    if not kls or kls == "0":
        logger.warning(f"Invalid 'kls' value: {kls}")
        return {"message": "Data not found: Invalid class value."}

    params = {
        "penempatan": penempatan,
        "kls": kls,
        "status": status,
        "limit": limit,
        "skip": skip,
    }
    headers = {"x-api-key": x_api_key}

    try:
        logger.info("Fetching Dasata data...")
        return await fetch_dasata(params=params, headers=headers)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_dasata_service: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
