from typing import List

from pydantic import BaseModel
from tortoise import Model, fields


class Recipient(BaseModel):
    recipient_type: str
    recipient_value: str


class NotificationData(BaseModel):
    from_module_id: int
    title: str
    description: str


class NotificationCreate(BaseModel):
    from_module_id: int
    title: str
    description: str
    recipients: List[Recipient]


class Module(Model):
    module_id = fields.IntField(pk=True)
    module_name = fields.CharField(max_length=100)
    module_url = fields.CharField(max_length=255)

    class Meta:
        table = "modules"


class Notifications(Model):
    notification_id = fields.IntField(pk=True)
    from_module = fields.ForeignKeyField(
        "models.Module", related_name="notifications", on_delete=fields.CASCADE
    )
    title = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "notifications"


class NotificationRecipient(Model):
    notification_recipient_id = fields.IntField(pk=True)
    notification = fields.ForeignKeyField(
        "models.Notifications",
        related_name="notification_recipients",
        on_delete=fields.CASCADE,
    )
    recipient_type = fields.CharField(
        max_length=10, choices=["ALL", "DIVISI", "BAGIAN", "USER"]
    )
    recipient_value = fields.CharField(max_length=50, null=True)

    class Meta:
        table = "notification_recipients"


class FallbackNotification(Model):
    id = fields.IntField(pk=True)
    fallback_id = fields.CharField(max_length=255)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    user_email = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    notification = fields.ForeignKeyField(
        "models.Notifications",
        related_name="fallback_notifications",
        null=True,
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "fallback_notifications"
