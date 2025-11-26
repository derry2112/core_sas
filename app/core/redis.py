import os

import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

redis_client = redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")


async def check_redis():
    try:
        redis_client.ping()
        print("Redis is connected.")
    except redis.exceptions.ConnectionError:
        print("Redis connection failed.")
    except Exception as e:
        print(f"An error occurred: {e}")


async def close_redis():
    try:
        redis_client.close()
        print("Redis connection closed.")
    except Exception as e:
        print(f"Error while closing Redis connection: {e}")
