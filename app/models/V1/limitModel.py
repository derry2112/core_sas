from fastapi import Query
from pydantic import BaseModel, EmailStr


class UserRequest(BaseModel):
    email: EmailStr
    limit: int = Query(..., gt=0)
