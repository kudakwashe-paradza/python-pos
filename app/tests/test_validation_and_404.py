
import pytest

from core.security import create_access_token



INVALID_CREATE_PAYLOADS = {
    "/categories/": {},  
    "/customers/": {"first_name": "Jane"},  
    "/products/": {"product_name": "Paracetamol"},  
    "/suppliers/": {},  
    "/users/": {"user_name": "nouser"},  
    "/sales/": {},  
    "/payments/": {"payment_method": "cash"}, 
    "/sale-items/": {"quantity_sold": 1},  
    "/receipts/": {"receipt_number": "RCPT-1"},  
    "/inventory/": {},  
}


MISSING_RESOURCE_PATHS = [
    "/categories/999999",
    "/customers/999999",
    "/products/999999",
    "/suppliers/999999",
    "/users/999999",
    "/sales/999999",
    "/payments/999999",
    "/sale-items/999999",
    "/receipts/999999",
    "/inventory/999999",
]


@pytest.mark.parametrize("path, payload", INVALID_CREATE_PAYLOADS.items())
def test_create_with_missing_required_fields_returns_422(client, auth_headers, path, payload):
    response = client.post(path, json=payload, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.parametrize("path", MISSING_RESOURCE_PATHS)
def test_get_nonexistent_resource_returns_404(client, auth_headers, path):
    response = client.get(path, headers=auth_headers)
    assert response.status_code == 404


def test_create_category_succeeds_with_valid_payload(client, auth_headers):
    """Sanity check alongside the 422 cases: a well-formed payload is not
    rejected by the same validation that blocks the malformed ones."""
    response = client.post(
        "/categories/",
        json={"category_name": "Antibiotics", "description": "Prescription only"},
        headers=auth_headers,
    )
    assert response.status_code == 201



def test_register_rejects_duplicate_username(db_session):

    from fastapi import HTTPException
    from schemas.user import UserCreate
    from services import auth_service

    payload = UserCreate(
        employee_code="EMP-DUP",
        user_name="duplicate_user",
        role="cashier",
        password="correct-horse-battery-staple",
    )
    auth_service.register(db_session, payload)

    with pytest.raises(HTTPException) as exc_info:
        auth_service.register(db_session, payload)
    assert exc_info.value.status_code == 400


def test_authenticate_rejects_wrong_password(db_session):
    from fastapi import HTTPException
    from schemas.user import UserCreate
    from services import auth_service

    auth_service.register(
        db_session,
        UserCreate(
            employee_code="EMP-WRONGPW",
            user_name="wrongpw_user",
            role="cashier",
            password="correct-password",
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenicate(db_session, "wrongpw_user", "incorrect-password")
    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_malformed_token(client):
    response = client.get(
        "/categories/", headers={"Authorization": "Bearer not-a-real-jwt"}
    )
    assert response.status_code == 401


def test_get_current_user_rejects_token_for_inactive_user(client, db_session):
    from models.user import User

    user = User(
        employee_code="EMP-INACTIVE",
        user_name="inactive_user",
        role="cashier",
        password_hash="irrelevant",
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(user.id)
    response = client.get(
        "/categories/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
