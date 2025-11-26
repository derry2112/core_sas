from typing import List

from pydantic import BaseModel
from tortoise import fields, models


class PermissionResponse(BaseModel):
    id: int
    action: str
    subject: str


class RoleResponse(BaseModel):
    id: int
    name: str
    permissions: List[PermissionResponse]


class Role(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "roles"


class Permission(models.Model):
    id = fields.IntField(pk=True)
    action = fields.CharField(max_length=255)
    subject = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "permissions"


class PermissionRole(models.Model):
    role = fields.ForeignKeyField("models.Role", related_name="permissions")
    permission = fields.ForeignKeyField("models.Permission", related_name="roles")

    class Meta:
        table = "permission_role"
        unique_together = (("role", "permission"),)
