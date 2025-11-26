from fastapi import HTTPException

from app.api.gateway.sarpras.sarprasEntity import fetch_kendaraan, fetch_ruangan
from app.core.logging import logger


async def get_ruangan_service(page: int, limit: int):
    params = {"page": page, "limit": limit}

    try:
        response = await fetch_ruangan(params=params)
        return {"success": True, "data": response}
    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_kendaraan_service(page: int, limit: int):
    params = {"page": page, "limit": limit}

    try:
        response = await fetch_kendaraan(params=params)
        return {"success": True, "data": response}
    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
