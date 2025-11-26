import httpx
import pytz
from fastapi import HTTPException
from datetime import datetime

from app.api.crypto.cryptoEntity import encrypt_data
from app.models.V1.models import User

headers = {
    "User-Agent": "Mozilla/5.0 ... Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://cmspenaburs.bpkpenaburjakarta.sch.id",
    "Referer": "https://cmspenaburs.bpkpenaburjakarta.sch.id/",
    "Cookie": "lng=en",
}


def generate_key(userid: str) -> str:
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    now = datetime.now(jakarta_tz)
    dt = now.strftime("%Y%m%d%H%M%S")
    return userid + dt


async def penaburs(user_data: dict):
    try:
        email = user_data["email"]
        user = await User.get_or_none(email_penabur=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        nik = user.nik
        timestamp = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y%m%d%H%M%S")
        key = generate_key(nik)
        encrypted_email = encrypt_data(email)

        form_data = {
            "email": encrypted_email,
            "key": key,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://cmspenaburs.bpkpenaburjakarta.sch.id/api/auth/generate-token",
                data=form_data,
                headers=headers,
            )

        if response.status_code == 200:
            try:
                response_data = response.json()
                if "token" in response_data:
                    redirect_url = (
                        "https://penaburs.bpkpenaburjakarta.sch.id/auth/sas"
                        f"?token={response_data['token']}"
                    )
                    return {
                        "success": True,
                        "token": response_data["token"],
                        "message": "Authentication successful",
                        "email": email,
                        "redirect_url": redirect_url,
                        "timestamp": timestamp,
                    }
                raise HTTPException(status_code=401, detail="Token not found.")
            except ValueError:
                raise HTTPException(status_code=502, detail="Invalid response format.")

        raise HTTPException(
            status_code=502,
            detail=f"Authentication server error. Status: {response.status_code}",
        )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to authentication server: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


async def best(user_data: dict):
    try:
        email = user_data["email"]
        user = await User.get_or_none(email_penabur=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        nik = user.nik
        now = datetime.now(pytz.timezone("Asia/Jakarta"))
        timestamp = now.strftime("%Y%m%d%H%M%S")
        generated_key = nik + timestamp
        encrypted_email = encrypt_data(email)

        form_data = {
            "email": (None, encrypted_email),
            "key": (None, generated_key),
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://cmspenaburs.bpkpenaburjakarta.sch.id/api/auth/generate-token",
                files=form_data,
                headers=headers,
            )

        if response.status_code == 200:
            try:
                response_data = response.json()
                if "token" in response_data:
                    redirect_url = (
                        "https://penaburs.bpkpenaburjakarta.sch.id/auth/sas"
                        f"?token={response_data['token']}"
                    )
                    return {
                        "success": True,
                        "token": response_data["token"],
                        "message": "Authentication successful",
                        "email": email,
                        "redirect_url": redirect_url,
                        "timestamp": timestamp,
                    }
                raise HTTPException(status_code=401, detail="Token not found.")
            except ValueError:
                raise HTTPException(status_code=502, detail="Invalid response format.")

        raise HTTPException(
            status_code=502,
            detail=f"Authentication server error. Status: {response.status_code}",
        )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to authentication server: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
