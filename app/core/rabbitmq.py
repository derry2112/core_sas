import asyncio
import json
import os

import aio_pika

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "admin_rabbitmqxsas")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq_service")
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:5672/"


async def get_rabbit_connection(retries: int = 5):
    for attempt in range(retries):
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            return connection
        except Exception:

            await asyncio.sleep(2**attempt)
    return None


async def publish_message(routing_key: str, message: dict):
    connection = await get_rabbit_connection()
    if not connection:
        print("Could not establish a connection to RabbitMQ.")
        return

    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=routing_key,
        )
