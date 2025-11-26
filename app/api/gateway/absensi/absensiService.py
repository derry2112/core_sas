import json

from fastapi import HTTPException, Response

from app.api.gateway.absensi.absensiEntity import fetch_absen_tgl
from app.core.apiUrl import ABSENSI_API_KEY
from app.core.logging import logger


async def get_absensi_loc_service(
    bulan: str,
    tahun: str,
    lokasi_penggajian: str,
    limit: int,
    skip: int,
    x_api_key: str,
) -> Response:
    if x_api_key != ABSENSI_API_KEY:
        logger.error("Forbidden: Invalid API key")
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API key")

    params = {
        "bulan": bulan,
        "tahun": tahun,
        "lokasi_penggajian": lokasi_penggajian,
        "limit": limit,
        "offset": skip,
    }
    headers = {"x-api-key": ABSENSI_API_KEY}

    try:
        data = await fetch_absen_tgl(params=params, headers=headers)
        return Response(content=json.dumps(data), media_type="application/json")
    except HTTPException as e:
        logger.error(f"Error fetching absensi: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
