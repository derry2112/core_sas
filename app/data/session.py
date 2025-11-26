from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.cores.config import settings

DATABASE_URL = (
    f"mysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}/{settings.DB_NAME}"
)

engine = create_engine(
    DATABASE_URL, pool_size=settings.DB_CONNECTION_LIMIT, max_overflow=0
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
