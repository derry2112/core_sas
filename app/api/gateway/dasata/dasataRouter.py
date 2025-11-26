from fastapi import APIRouter, Header, HTTPException

from app.api.gateway.dasata.dasataService import get_dasata_service
from app.core.logging import logger

router = APIRouter()


@router.get("/pembayaran", response_model=dict)
async def get_dasata_endpoint(
    penempatan: str,
    kls: str,
    status: str,
    limit: int = 10,
    skip: int = 0,
    x_api_key: str = Header(...),
):
    try:
        response = await get_dasata_service(
            penempatan, kls, status, limit, skip, x_api_key
        )

        if "message" in response:
            logger.info(f"Data not found for kls={kls}: {response['message']}")
            return response

        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in /pembayaran endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
