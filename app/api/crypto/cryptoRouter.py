import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr

from app.api.crypto.cryptoEntity import decrypt_data, encrypt_data

load_dotenv()

router = APIRouter()


class EncryptRequest(BaseModel):
    data: constr(min_length=8)


class DecryptRequest(BaseModel):
    encrypted_data: constr(min_length=8)


@router.post("/generate-key/")
async def generate_key_endpoint():
    new_key = Fernet.generate_key().decode()
    os.environ["SECRET_KEY"] = new_key
    return JSONResponse(content={"secret_key": new_key})


@router.post("/encrypt/")
async def encrypt_endpoint(data: str):
    encrypted = encrypt_data(data)
    return JSONResponse(content={"encrypted_data": encrypted})


@router.post("/decrypt/")
async def decrypt_endpoint(encrypted_data: str):
    decrypted = decrypt_data(encrypted_data)
    return JSONResponse(content={"decrypted_data": decrypted})
