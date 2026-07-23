from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL
from database.models import Base

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """ينشئ الجداول لو مش موجودة."""
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
