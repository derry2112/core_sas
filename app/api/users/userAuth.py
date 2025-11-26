from datetime import datetime, timedelta
from typing import Optional

import jwt
from clerk_backend_api.jwks_helpers.verifytoken import VerifyTokenOptions, verify_token
from fastapi import Depends, HTTPException, Request, Response
from fastapi.security.utils import get_authorization_scheme_param

from app.core.clerk import CLERK_SECRET_KEY
from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)
from app.core.logging import logger
from app.models.V1.models import User as ORMUser
from app.models.V1.roleModel import PermissionRole, Role


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_clerk_token_header(request: Request):
    auth = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(auth)

    if scheme.lower() != "bearer" or not token:
        logger.warning("Authorization header missing or invalid")
        raise HTTPException(
            status_code=401, detail="Authorization header missing or invalid"
        )

    try:
        verify_options = VerifyTokenOptions(secret_key=CLERK_SECRET_KEY)
        verified_token = verify_token(token, verify_options)

        email = verified_token.get("email_addresses", [None])[0] or verified_token.get(
            "email"
        )
        logger.info(f"Verified token payload: email: {email}")

        if not email:
            logger.warning("Email not found in token payload")
            raise HTTPException(status_code=401, detail="Email not found in token")

        return email

    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


async def update_user_activity(user_email: str):
    db_user = await ORMUser.filter(email_penabur=user_email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.last_login = datetime.utcnow()
    await db_user.save()
    return db_user


async def login_with_firebase(request: Request, response: Response):
    user_email = verify_clerk_token_header(request)
    db_user = await ORMUser.filter(email_penabur=user_email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Email not registered in system")

    role = await Role.get_or_none(id=db_user.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    permissions = (
        await PermissionRole.filter(role_id=role.id).select_related("permission").all()
    )

    permission_list = [
        {"action": p.permission.action, "subject": p.permission.subject}
        for p in permissions
    ]

    user_data = {
        "sub": db_user.email_penabur,
        "nik": db_user.nik,
        "name": db_user.nama,
        "penempatan": db_user.penempatan,
        "jabatan": db_user.jabatan,
        "role": role.name,
        "permissions": permission_list,
    }

    access_token = create_access_token(data=user_data)
    refresh_tok = create_refresh_token(data=user_data)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=int(ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_tok,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=int(REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60),
    )

    await update_user_activity(user_email)

    return {
        "user": {
            "nik": db_user.nik,
            "name": db_user.nama,
            "penempatan": db_user.penempatan,
            "jabatan": db_user.jabatan,
        },
        "role": {"name": role.name, "permissions": permission_list},
    }


async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token required")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        db_user = await ORMUser.filter(email_penabur=user_email).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        role = await Role.get_or_none(id=db_user.role_id)
        user_data = {
            "sub": db_user.email_penabur,
            "nik": db_user.nik,
            "name": db_user.nama,
            "penempatan": db_user.penempatan,
            "jabatan": db_user.jabatan,
            "role": role.name,
        }

        access_token = create_access_token(data=user_data)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=int(ACCESS_TOKEN_EXPIRE_MINUTES * 60),
        )

        return {"access_token": access_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


async def get_user_me(user_email: dict = Depends(verify_clerk_token_header)):
    db_user = await ORMUser.filter(email_penabur=user_email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "nik": db_user.nik,
        "name": db_user.nama,
        "penempatan": db_user.penempatan,
        "jabatan": db_user.jabatan,
    }


async def logout_and_revoke_token(
    request: Request,
    response: Response,
    user_email: dict = Depends(verify_clerk_token_header),
):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Successfully logged out."}
