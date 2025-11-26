from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator
from tortoise import fields
from tortoise.models import Model

from app.models.V1.roleModel import RoleResponse


class UserRequest(BaseModel):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str
    role: RoleResponse


class RevokeTokenRequest(BaseModel):
    email: EmailStr
    token: str


class UserInDB(BaseModel):
    nik: int
    email_penabur: str
    jabatan: str = None
    penempatan: str
    nama: str
    flag_aktif: bool
    created_at: datetime
    updated_at: datetime
    role_id: int

    class Config:
        from_attributes = True

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, value):
        """Convert ISO formatted datetime strings to datetime objects."""
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value


class User(Model):
    id_user = fields.IntField(pk=True)
    nik = fields.CharField(max_length=10, unique=True)
    email_penabur = fields.CharField(max_length=255, null=True)
    jabatan = fields.CharField(max_length=5, null=True)
    penempatan = fields.CharField(max_length=255)
    nama = fields.CharField(max_length=255)
    flag_aktif = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)
    role = fields.ForeignKeyField("models.Role", related_name="users", null=True)

    class Meta:
        table = "users"


class UserCreate(UserInDB):
    pass


class UserUpdate(UserInDB):
    pass


class UserOut(UserInDB):
    id_user: int
    email_penabur: str
    created_at: datetime
    updated_at: datetime
