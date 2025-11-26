from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute


class ClerkAuthMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, request: Request):
        token = request.headers.get("Authorization")
        if token is None:
            return JSONResponse(
                content={"detail": "Authorization token missing"}, status_code=401
            )
        try:
            user_info = verify_clerk_token(token)
            request.state.user = user_info
            return await self.app(request)
        except HTTPException as e:
            return JSONResponse(content={"detail": e.detail}, status_code=e.status_code)


app.add_middleware(ClerkAuthMiddleware)
