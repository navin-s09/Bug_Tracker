from datetime import datetime

from app.models.enums import UserRole
from app.models.user import User


def test_user_model():
    user = User(
        email="developer@fulcrumdigital.com",
        hashed_password="hashed-password",
    )

    assert user.email == "developer@fulcrumdigital.com"
    assert user.hashed_password == "hashed-password"


def test_user_role_enum():
    assert UserRole.MANAGER.value == "manager"
    assert UserRole.LEAD.value == "lead"
    assert UserRole.DEV.value == "dev"
    assert UserRole.CLIENT.value == "client"


def test_user_default_role():
    user = User(
        email="developer@fulcrumdigital.com",
        hashed_password="hashed-password",
    )

    # SQLAlchemy applies Python-side defaults when the object
    # is inserted/flushed, so inspect the column default here.
    role_column = User.__table__.columns["role"]

    assert role_column.default is not None


def test_user_created_at_default():
    created_at_column = User.__table__.columns["created_at"]

    assert created_at_column.default is not None


def test_user_table_name():
    assert User.__tablename__ == "users"


def test_user_required_fields():
    columns = User.__table__.columns

    assert columns["email"].nullable is False
    assert columns["hashed_password"].nullable is False
    assert columns["role"].nullable is False
    assert columns["created_at"].nullable is False