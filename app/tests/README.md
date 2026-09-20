# POS API test suite

Runs against an in-memory SQLite database (see `conftest.py`), so no
Postgres instance is needed to run these.

## Setup

```bash
pip install fastapi "sqlalchemy>=2.0" pydantic pyjwt "pwdlib[argon2]" \
    httpx pytest psycopg2-binary
```

`psycopg2-binary` is needed only because `database.py` builds a Postgres
engine at import time even for tests — it's never actually connected to.

## Run

```bash
pytest -v
```

## How to read the results

Every test is either a normal pass/fail, or marked `xfail(strict=True)`
with a `reason=` pointing at the specific bug it documents (from the
earlier code review). That gives you two things at once:

1. **A clean `pytest` run today** — 13 passed, 20 xfailed, 0 failed —
   even though the underlying code has real bugs.
2. **A to-do list with a tripwire.** When you fix a bug, its test starts
   *passing* instead of *xfailing*, and because the marker is
   `strict=True`, pytest turns that into a hard failure (`XPASS`) until
   you delete the `@pytest.mark.xfail(...)` decorator. You can't
   accidentally leave a fixed bug "documented" as still broken.

### Bugs currently pinned by an xfail test

| File | Bug | Test |
|---|---|---|
| `core/security.py` | `jwt_algorithm = "H256"` isn't a real algorithm; `create_access_token` always raises | `test_security.py::test_create_access_token_succeeds` |
| `repositories/user_repository.py` | `get_by_user_name` calls `db.get(User).filter(...)`, which isn't valid | `test_user_repository.py::test_get_by_user_name_finds_existing_user` |
| `repositories/user_repository.py` | `get_by_id` requires an extra `user_id` arg no caller passes, and filters on nonexistent `User.user_id` | `test_user_repository.py::test_get_by_id_matches_the_calling_convention_used_by_auth_service` |
| `repositories/product_repository.py` | `update()`'s commit/refresh/return sit inside the loop, so only the first field in a multi-field update is applied | `test_product_repository.py::test_update_applies_multiple_fields_in_one_call` |
| `services/auth_service.py` | writes/reads `hashed_password`, but the `User` model's column is `password_hash` | `test_auth_and_user_service.py::test_register_creates_user_with_hashed_password`, `test_register_then_authenticate_round_trip`, `test_authenticate_rejects_unknown_username` |
| `services/user_service.py` | `create_user` stores the plaintext password in `password_hash` instead of hashing it | `test_auth_and_user_service.py::test_create_user_hashes_the_password` |
| `routers/*.py` | only `products` requires `get_current_user`; every other router (users, sales, payments, customers, suppliers, inventory, receipts, sale-items) is unauthenticated | `test_router_auth.py::test_other_endpoints_should_also_reject_unauthenticated_requests[...]` (11 cases) |

### What's confirmed working (real passing tests, not xfail)

- Password hashing round-trip (`hash_password` / `verify_password`)
- Full CRUD lifecycle for `category`, `customer`, `supplier` services
- 404 handling for missing rows across those services
- `Product` → `Inventory` and `User` → `Sale` → `SaleItem`/`Payment`/`Receipt`
  creation chains
- `products` router correctly rejecting unauthenticated requests

## Structure

```
tests/
  test_security.py            core/security.py
  test_user_repository.py     repositories/user_repository.py
  test_product_repository.py  repositories/product_repository.py
  test_auth_and_user_service.py  services/auth_service.py, user_service.py
  test_crud_services.py       category/customer/supplier services (generic pattern)
  test_relational_crud.py     product+inventory, user+sale+sale_item+payment+receipt
  test_router_auth.py         which routers require a token, via real HTTP calls
```
