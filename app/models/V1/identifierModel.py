from tortoise import fields
from tortoise.models import Model


class UserAuthIdentifier(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()
    last_login = fields.DatetimeField(auto_now_add=True, null=True)
    user_agent = fields.CharField(max_length=255)
    ip_address = fields.CharField(max_length=255)
    device_id = fields.CharField(max_length=36, unique=True, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_auth_identifier"
