"""Base declarativa, motor y sesiones de SQLAlchemy."""
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def url_sqlalchemy(url: str) -> str:
    """La configuración usa 'postgresql://'; SQLAlchemy necesita indicar psycopg 3."""
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


def crear_motor(url: str) -> Engine:
    return create_engine(url_sqlalchemy(url), pool_pre_ping=True)


def crear_sesiones(motor: Engine) -> sessionmaker[Session]:
    return sessionmaker(motor, expire_on_commit=False)
