from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

DATABASE_URL = settings.database_url

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured. "
        "Set it in backend/.env before starting the backend."
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
