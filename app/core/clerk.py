import os

from dotenv import load_dotenv

load_dotenv()

CLERK_BASE_URL = os.getenv("CLERK_BASE_URL")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
