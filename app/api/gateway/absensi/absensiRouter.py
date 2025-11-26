from fastapi import APIRouter, Header

from app.api.gateway.absensi.absensiService import get_absensi_loc_service

router = APIRouter()


@router.get("/transaksi-absen-tanggal", response_model=dict)
async def get_absensi_tgl(
    bulan: str,
    tahun: str,
    lokasi_penggajian: str,
    limit: int = 10,
    skip: int = 0,
    x_api_key: str = Header(...),
):
    return await get_absensi_loc_service(
        bulan, tahun, lokasi_penggajian, limit, skip, x_api_key
    )
