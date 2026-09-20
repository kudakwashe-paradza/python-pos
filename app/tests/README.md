# POS API test suite

Runs against an in-memory SQLite database (see `conftest.py`), so no
Postgres instance is needed and the real development database is never
touched.

## Setup

From the repository root:

```bash
pip install -r requirements.txt
```

## Run

```bash
cd app
pytest -v
```

All 66 tests pass. For a coverage report:

```bash
pytest --cov=. --cov-report=term-missing
```

## Structure

```
tests/
  test_security.py             core/security.py — password hashing, JWT create/decode
  test_user_repository.py      repositories/user_repository.py
  test_product_repository.py   repositories/product_repository.py
  test_auth_and_user_service.py  services/auth_service.py, user_service.py —
                                  register, authenticate, hashed password storage
  test_crud_services.py        full create/get/list/update/delete lifecycle for
                                category, customer, supplier + 404 on missing rows
  test_extended_crud.py        update/delete for product, inventory, sale,
                                sale_item, payment, receipt, user
  test_relational_crud.py      Product -> Inventory, and User -> Sale ->
                                SaleItem/Payment/Receipt creation chains
  test_router_auth.py          every router correctly rejects requests with no token
  test_validation_and_404.py   422 on malformed create payloads (every entity),
                                404 on missing resources (every entity), and auth
                                failure scenarios: wrong password, duplicate
                                username, malformed token, deactivated user's token
```

## Fixtures (`conftest.py`)

- `engine` — a fresh in-memory SQLite engine per test, with all tables created
- `db_session` — a SQLAlchemy session bound to that engine, for calling
  service functions directly
- `client` — a `TestClient` with `get_db` overridden to use the same
  in-memory engine, for exercising real HTTP routes
- `auth_headers` — inserts an active user and mints a real JWT for it, so
  HTTP tests can call routes that require `get_current_user`

## What's covered

- **Successful CRUD** for all ten entities (categories, customers,
  suppliers, products, inventory, sales, sale items, payments, receipts,
  users)
- **Validation errors (422)** on malformed create requests, sent through
  real HTTP calls for every entity
- **Missing resources (404)** for every entity's get-by-id route
- **Auth failure scenarios**: no token, malformed token, wrong password,
  duplicate username on registration, and a deactivated user's token
  being rejected with 403

## Known gap

There's no `/auth/register` or `/auth/login` route wired up in `main.py`
yet — `dependencies.py`'s `OAuth2PasswordBearer` points at `auth/login`,
but no router exposes it. `test_validation_and_404.py`'s auth tests call
`services/auth_service.py` directly rather than through HTTP for this
reason. Once an auth router exists, those tests should be extended (or
duplicated) to hit it over HTTP as well.
