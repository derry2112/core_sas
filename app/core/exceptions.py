from typing import Optional


class AuthenticationError(Exception):
    def __init__(
        self, message: str = "Authentication failed", details: Optional[dict] = None
    ):
        self.message = message
        self.details = details or {}

    def __str__(self):
        return f"{self.message} - {self.details}"
