from fastapi import APIRouter, Depends, Request, Response


from app.api.users.userAuth import (
    login_with_firebase,
    logout_and_revoke_token,
    refresh_token,
)
from app.services.jwtMiddleware import require_auth

router = APIRouter()


@router.post("/token")
async def token_endpoint(request: Request, response: Response):
    return await login_with_firebase(request, response)


@router.post("/refresh")
async def refresh_endpoint(request: Request, response: Response):
    return await refresh_token(request, response)


@router.get("/me")
async def get_me(user_data=Depends(require_auth)):
    return {"message": "Authenticated", "user": user_data}


@router.post("/logout")
async def logout(
    request: Request, response: Response, user_email: str = Depends(require_auth)
):
    # async def logout(response: Response, user_data = Depends(require_auth)):
    #    response.delete_cookie("access_token")
    #    response.delete_cookie("refresh_token")
    #    return {"message": f"Logout successful for {user_data['email']}"}
    return logout_and_revoke_token(request, response, user_email)
