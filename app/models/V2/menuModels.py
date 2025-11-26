from tortoise import fields
from tortoise.models import Model


class AdminMenu(Model):
    id = fields.IntField(pk=True)
    nameUrl = fields.CharField(max_length=255)
    file_path = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True, null=True)
    deleted_at = fields.DatetimeField(null=True)
