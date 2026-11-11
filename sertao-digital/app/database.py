import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

DEFAULT_DATABASE_URL = "sqlite:///./sertao_digital.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
is_sqlite = DATABASE_URL.startswith("sqlite")
is_postgres = DATABASE_URL.startswith("postgresql")

engine_kwargs = {}

if is_sqlite:
    engine_kwargs.update(
        {
            "connect_args": {"check_same_thread": False},
            "poolclass": NullPool,
        }
    )
else:
    engine_kwargs.update(
        {
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 5,
            "connect_args": {
                "connect_timeout": 5,
                # Evita que uma requisição fique presa indefinidamente em locks/SQL.
                "options": "-c lock_timeout=10000 -c statement_timeout=15000",
            },
        }
    )

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
