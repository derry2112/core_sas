from pydantic import BaseModel


class HashInput(BaseModel):
    text: str


class HashVerifyInput(BaseModel):
    text: str
    hash_value: str
