"""Engine SQLAlchemy com classes OO, type hints e dependência geradora por requisição."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Base declarativa comum às tabelas que o Alembic versiona."""


def _create_database_engine() -> Engine:
    """Monta o engine tipado; SQLite recebe configuração extra para uso multithread."""

    url = get_settings().database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


engine = _create_database_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Usa um generator tipado como dependência FastAPI e sempre fecha a sessão."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
