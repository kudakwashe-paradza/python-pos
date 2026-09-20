"""
repositories/user_repository.py

get_by_user_name() looks up a user by username; get_by_id() looks a user
up by primary key, matching the two-argument call auth_service.get_user_from_token
actually uses.
"""
from models.user import User
from repositories.user_repository import user_repository


def seeded_user_fixture(db_session):
    user = User(
        employee_code="EMP-100",
        user_name="cashier1",
        role="cashier",
        password_hash="already-hashed",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_get_by_user_name_finds_existing_user(db_session):
    seeded_user = seeded_user_fixture(db_session)
    found = user_repository.get_by_user_name(db_session, "cashier1")
    assert found is not None
    assert found.id == seeded_user.id


def test_get_by_user_name_returns_none_for_unknown_username(db_session):
    assert user_repository.get_by_user_name(db_session, "nobody") is None


def test_get_by_id_matches_the_calling_convention_used_by_auth_service(db_session):
    seeded_user = seeded_user_fixture(db_session)
    found = user_repository.get_by_id(db_session, seeded_user.id)
    assert found is not None
    assert found.user_name == "cashier1"
