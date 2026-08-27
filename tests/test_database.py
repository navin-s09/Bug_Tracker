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


def test_users_table_columns():
    create_tables()

    inspector = inspect(engine)

    columns = inspector.get_columns("users")

    column_names = {column["name"] for column in columns}

    assert {
        "id",
        "email",
        "hashed_password",
        "role",
        "created_at",
    }.issubset(column_names)


def test_users_email_is_unique():
    create_tables()

    inspector = inspect(engine)

    unique_constraints = inspector.get_unique_constraints("users")

    unique_columns = {
        column
        for constraint in unique_constraints
        for column in constraint["column_names"]
    }

    assert "email" in unique_columns


def test_users_role_is_not_nullable():
    create_tables()

    inspector = inspect(engine)

    columns = {
        column["name"]: column
        for column in inspector.get_columns("users")
    }

    assert columns["role"]["nullable"] is False