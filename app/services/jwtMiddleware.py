from datetime import datetime
from typing import Dict

from clerk_backend_api.jwks_helpers.verifytoken import VerifyTokenOptions, verify_token
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.clerk import CLERK_SECRET_KEY
from app.core.exceptions import AuthenticationError
from app.core.logging import logger

security = HTTPBearer(auto_error=True)


class ClerkAuth:
    def __init__(self):
        self.clerk_secret = CLERK_SECRET_KEY
        if not self.clerk_secret:
            raise ValueError("CLERK_SECRET_KEY environment variable is not set")

    async def verify_session_token(
        self,
        credentials: HTTPAuthorizationCredentials = Security(security),
    ) -> Dict:
        try:
            options = VerifyTokenOptions(secret_key=self.clerk_secret)
            payload = verify_token(credentials.credentials, options)
            logger.debug(f"Token payload: {payload}")
            if not payload.get("sub"):
                raise AuthenticationError(
                    message="Invalid token: missing required claims",
                    details={
                        "required_claims": ["sub"],
                        "received_claims": list(payload.keys()),
                    },
                )

            user_data = {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "session_id": payload.get("sid"),
                "expires_at": (
                    datetime.fromtimestamp(payload.get("exp"))
                    if payload.get("exp")
                    else None
                ),
            }

            logger.debug(f"Successfully verified token for user: {user_data}")
            return user_data

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError(
                message="Invalid authentication credentials",
                details={"error": str(e)},
            )

    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Security(security),
    ) -> Dict:
        return await self.verify_session_token(credentials)


auth = ClerkAuth()
require_auth = auth.__call__
