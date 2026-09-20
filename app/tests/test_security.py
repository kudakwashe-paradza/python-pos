"""
core/security.py

Password hashing round-trips correctly. Token creation currently does not:
jwt_algorithm is set to "H256", which is not a real algorithm name (PyJWT
only knows "HS256"). This means create_access_token() raises for every
call, which means /auth/login and get_current_user can never succeed.
"""
import pytest

from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_hash_password_does_not_store_plaintext():
    hashed = hash_password("s3cret!")
    assert hashed != "s3cret!"


def test_verify_password_accepts_correct_password():
    hashed = hash_password("s3cret!")
    assert verify_password("s3cret!", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("s3cret!")
    assert verify_password("wrong-password", hashed) is False


def test_create_access_token_succeeds():
    token = create_access_token(user_id=1)
    assert isinstance(token, str) and token


def test_create_and_decode_access_token_roundtrip():
    token = create_access_token(user_id=42)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
