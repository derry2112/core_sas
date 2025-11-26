from fastapi import HTTPException

from app.api.gateway.files.filesEntity import fetch_files


async def get_files_service(limit: int, skip: int):

    params = {"limit": limit, "skip": skip}

    try:
        response = await fetch_files(params=params)
        return {"response": response}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
