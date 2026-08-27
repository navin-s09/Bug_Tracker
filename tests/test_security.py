from app.core.security import hash_password, verify_password


def test_password_is_hashed():
    password = "StrongPassword123!"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert len(hashed_password) > 0


def test_password_verification_success():
    password = "StrongPassword123!"

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_password_verification_failure():
    password = "StrongPassword123!"

    hashed_password = hash_password(password)

    assert verify_password("WrongPassword123!", hashed_password) is False