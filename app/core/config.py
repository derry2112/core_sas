import os
import secrets

from dotenv import load_dotenv
from tortoise import Tortoise
from tortoise.exceptions import ConfigurationError

from app.core.logging import logger

# Load environment variables from the .env file
load_dotenv()

# Store
STORE_KEY = os.getenv("STORE_KEY")

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(64)
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for the application.")

JWT_KEY = os.getenv("JWT_SECRET")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
VALID_EMAIL_DOMAIN = os.getenv("VALID_EMAIL_DOMAIN")

# PostgreSQL configurations
DATABASE_URL = (
    f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Redis configurations
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

# Tortoise ORM configurations
TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "app.models.V1.models",
                "app.models.V1.roleModel",
                "app.models.V1.identifierModel",
                "app.models.V1.notifModel",
                "app.models.V2.menuModels",
            ],
            "default_connection": "default",
        }
    },
}


async def init_db():
    """Initialize Tortoise ORM and generate schema."""
    try:
        logger.debug("TORTOISE_ORM configuration: %s", TORTOISE_ORM)
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas(safe=True)  # Generate schemas
        logger.debug(f"Database: {DATABASE_URL}")
        logger.info("Database connected and schemas created successfully.")
    except ConfigurationError as e:
        logger.error("Tortoise ORM Configuration error: %s", str(e))
        raise
    except Exception as e:
        logger.error("An error occurred while initializing the database: %s", str(e))
        raise


# Main execution for standalone script
if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())
