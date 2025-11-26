from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException, Request, Response, status
from jose import JWTError

from app.api.crypto.cryptoEntity import decrypt_data, encrypt_data
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.models.V1.models import User as ORMUser
from app.models.V1.roleModel import PermissionRole, Role
from app.services.auth import (
    add_to_blacklist,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)


async def refresh_token(request: Request, response: Response):
    refresh_token_value = request.cookies.get("refresh_token")

    if not refresh_token_value:
        raise HTTPException(status_code=401, detail="Refresh token cookie not found")

    payload = await verify_refresh_token(refresh_token_value)
    email = decrypt_data(payload.get("sub"))

    db_user = await ORMUser.filter(email_penabur=email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    role = await Role.filter(id=db_user.role_id).first()
    permissions = (
        await PermissionRole.filter(role_id=role.id).select_related("permission").all()
    )
    permission_list = [
        {"action": p.permission.action, "subject": p.permission.subject}
        for p in permissions
    ]

    new_access_token = create_access_token(data={"sub": encrypt_data(email)})
    new_refresh_token = create_refresh_token(data={"sub": encrypt_data(email)})

    device_id = str(uuid4())

    response.set_cookie(
        key="refresh_token_value",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS).total_seconds(),
    )
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds(),
    )

    return {
        "user": {
            "nik": db_user.nik,
            "name": db_user.nama,
            "penempatan": db_user.penempatan,
            "jabatan": db_user.jabatan,
        },
        "identifier": {
            "device_id": device_id,
        },
        "role": {"name": role.name, "permissions": permission_list},
    }


async def revoke_token(email: str, token: str):
    validate_token_presence(token)

    payload = await verify_and_get_payload(token)

    if payload.get("sub") != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email does not match the token.",
        )

    await get_user_by_email(email)
    await check_token_expiration(payload, token)

    await add_to_blacklist(token)
    return {"detail": "Token has been revoked"}


def validate_token_presence(token: str):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token not provided",
        )


async def verify_and_get_payload(token: str):
    try:
        return await verify_refresh_token(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc


async def get_user_by_email(email: str):
    db_user = await ORMUser.filter(email_penabur=email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return db_user


async def check_token_expiration(payload: dict, token: str):
    exp = payload.get("exp")
    if exp:
        expiration_time = datetime.fromtimestamp(exp, tz=timezone.utc)
        if expiration_time < datetime.now(timezone.utc):
            await add_to_blacklist(token)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has been revoked due to expiration",
            )
