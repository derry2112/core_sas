# from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.logging import logger


def setup_cors(app: FastAPI):
    origins = [
        "https://dt24ftxpcr79w.cloudfront.net",
        "http://localhost:5173",
        # "https://ticket-bpkpenaburjakarta.my.id",
    ]
    logger.debug(f"Setting up CORS with allowed origins: {origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,
    )
