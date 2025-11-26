# pylint: disable=C0116, W0613, C0303, C0301, C0305

from fastapi import HTTPException

from app.models.V1.models import User as ORMUser
from app.models.V1.roleModel import PermissionRole, Role


async def get_user(email: str) -> ORMUser:
    user = await ORMUser.filter(email_penabur=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user_role_and_permissions(user: ORMUser):
    role = await Role.filter(id=user.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    permissions = (
        await PermissionRole.filter(role_id=role.id).select_related("permission").all()
    )
    permission_list = [
        {
            "id": p.permission.id,
            "action": p.permission.action,
            "subject": p.permission.subject,
        }
        for p in permissions
    ]
    return role, permission_list
