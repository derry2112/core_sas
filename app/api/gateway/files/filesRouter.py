from fastapi import APIRouter

from app.api.gateway.files.filesService import get_files_service

router = APIRouter()


@router.get("/files", response_model=dict)
async def get_files_endpoint(
    limit: int = 10,
    skip: int = 0,
):
    return await get_files_service(limit, skip)
