from app.core.security import hash_password, verify_password


def test_password_hashing():
    password = "test-password"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("wrong-password", hashed_password)
    