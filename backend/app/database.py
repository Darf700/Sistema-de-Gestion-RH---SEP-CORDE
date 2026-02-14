from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Solo para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency para obtener sesion de DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Crear todas las tablas."""
    Base.metadata.create_all(bind=engine)
