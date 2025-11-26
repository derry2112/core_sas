import base64
import os
import secrets

from cryptography.fernet import Fernet
from fastapi import HTTPException

from app.core.config import STORE_KEY
from app.core.logging import logger


def get_secret_key():
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise HTTPException(
            status_code=404, detail="Secret key not found in environment variables."
        )
    return secret_key.encode()


def encrypt_data(data: str) -> str:
    try:
        salt = secrets.token_bytes(16)
        secret_key = STORE_KEY
        cipher_suite = Fernet(secret_key)

        encrypted_data = cipher_suite.encrypt(data.encode())

        padded_salt = salt * ((len(encrypted_data) // len(salt)) + 1)
        encrypted_with_salt = bytes(a ^ b for a, b in zip(encrypted_data, padded_salt))

        logger.info("Data encrypted successfully.")
        result = base64.urlsafe_b64encode(salt + encrypted_with_salt).decode()
        return result
    except Exception as e:
        logger.error("Encryption failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Encryption failed.")


def decrypt_data(encrypted_data: str) -> str:
    try:
        decoded = base64.urlsafe_b64decode(encrypted_data)
        salt = decoded[:16]
        encrypted_part = decoded[16:]

        secret_key = STORE_KEY
        cipher_suite = Fernet(secret_key)

        padded_salt = salt * ((len(encrypted_part) // len(salt)) + 1)
        decrypted_with_salt = bytes(a ^ b for a, b in zip(encrypted_part, padded_salt))

        original_data = cipher_suite.decrypt(decrypted_with_salt)

        logger.info("Data decrypted successfully.")
        return original_data.decode()
    except Exception as e:
        logger.error("Decryption failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Decryption failed.")
