from sqlalchemy import inspect, text

from app.db.database import Base, SessionLocal, engine
from app.db.init_db import create_tables


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        assert result.scalar() == 1


def test_database_session():
    db = SessionLocal()

    try:
        result = db.execute(text("SELECT 1"))

        assert result.scalar() == 1
    finally:
        db.close()


def test_base_exists():
    assert Base is not None


def test_users_table_exists():
    create_tables()

    inspector = inspect(engine)

    assert "users" in inspector.get_table_names()