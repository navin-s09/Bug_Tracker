from app.models.enums import UserRole
from app.models.user import User


def test_user_model():
    user = User(email="test@example.com")

    assert user.email == "test@example.com"
    assert user.id is None
    assert user.created_at is None


def test_user_role_enum():
    assert UserRole.MANAGER.value == "manager"
    assert UserRole.LEAD.value == "lead"
    assert UserRole.DEV.value == "dev"
    assert UserRole.CLIENT.value == "client"