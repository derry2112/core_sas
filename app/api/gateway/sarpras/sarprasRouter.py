from fastapi import APIRouter, Query

from app.api.gateway.sarpras.sarprasService import (
    get_kendaraan_service,
    get_ruangan_service,
)

router = APIRouter()


@router.get("/sarpras-ruangan", response_model=dict)
async def ruangan(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
):
    return await get_ruangan_service(page, limit)


@router.get("/sarpras-kendaraan", response_model=dict)
async def kendaraan(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
):
    return await get_kendaraan_service(page, limit)
