
import pytest
from fastapi import HTTPException

from schemas.user import UserCreate
from services import auth_service, user_service


def make_user_create(**overrides):
    data = dict(
        employee_code="EMP-001",
        user_name="jdoe",
        role="cashier",
        password="correct-horse-battery-staple",
    )
    data.update(overrides)
    return UserCreate(**data)


def test_register_creates_user_with_hashed_password(db_session):
    user = auth_service.register(db_session, make_user_create())
    assert user.password_hash != "correct-horse-battery-staple"


def test_register_then_authenticate_round_trip(db_session):
    auth_service.register(db_session, make_user_create())
    result = auth_service.authenicate(db_session, "jdoe", "correct-horse-battery-staple")
    assert "access_token" in result


def test_authenticate_rejects_unknown_username(db_session):
    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenicate(db_session, "nobody", "whatever")
    assert exc_info.value.status_code == 401


def test_create_user_hashes_the_password(db_session):
    user = user_service.create_user(db_session, make_user_create(user_name="asmith"))
    assert user.password_hash != "correct-horse-battery-staple"
