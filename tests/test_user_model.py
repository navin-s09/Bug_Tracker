from app.models.user import User
def test_user_model():
    user = User(email="test@example.com")
    assert user.email == "test@example.com"
    assert user.id is None
    assert user.created_at is None
