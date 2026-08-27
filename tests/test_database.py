from sqlalchemy import inspect, text

from app.db.database import Base, SessionLocal, engine
from app.db.init_db import create_tables
from app.models.enums import UserRole
from app.models.user import User


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


def test_user_role_persisted():
    create_tables()

    db = SessionLocal()

    try:
        user = User(
            email="role-test-uunique@example.com",
            hashed_password="test-hashed-password",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.role == UserRole.DEV
    finally:
        db.close()