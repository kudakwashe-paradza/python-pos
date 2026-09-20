"""
The category/customer/supplier services follow an identical, working
get/list/create/update/delete pattern with no foreign-key dependencies.
One parametrized test covers all three so a regression in any of them
(or in their generated schema) shows up immediately.
"""
import pytest
from fastapi import HTTPException

from schemas.category import CategoryCreate, CategoryUpdate
from schemas.customer import CustomerCreate, CustomerUpdate
from schemas.supplier import SupplierCreate, SupplierUpdate
from services import category_service, customer_service, supplier_service


CASES = [
    pytest.param(
        category_service,
        "category",
        "list_categories",
        CategoryCreate(category_name="Painkillers", description="OTC pain relief"),
        CategoryUpdate(description="Updated description"),
        id="category",
    ),
    pytest.param(
        customer_service,
        "customer",
        "list_customers",
        CustomerCreate(first_name="Jane", last_name="Doe", phone_number="0700000000"),
        CustomerUpdate(phone_number="0711111111"),
        id="customer",
    ),
    pytest.param(
        supplier_service,
        "supplier",
        "list_suppliers",
        SupplierCreate(company_name="Acme Pharma", phone_number="0722222222"),
        SupplierUpdate(company_name="Acme Pharma Ltd"),
        id="supplier",
    ),
]


@pytest.mark.parametrize("service, prefix, list_fn_name, create_data, update_data", CASES)
def test_crud_lifecycle(db_session, service, prefix, list_fn_name, create_data, update_data):
    created = getattr(service, f"create_{prefix}")(db_session, create_data)
    assert created.id is not None

    fetched = getattr(service, f"get_{prefix}")(db_session, created.id)
    assert fetched.id == created.id

    all_rows = getattr(service, list_fn_name)(db_session)
    assert any(row.id == created.id for row in all_rows)

    updated = getattr(service, f"update_{prefix}")(db_session, created.id, update_data)
    for field, value in update_data.model_dump(exclude_unset=True).items():
        assert getattr(updated, field) == value

    getattr(service, f"delete_{prefix}")(db_session, created.id)
    with pytest.raises(HTTPException) as exc_info:
        getattr(service, f"get_{prefix}")(db_session, created.id)
    assert exc_info.value.status_code == 404


@pytest.mark.parametrize(
    "service, id_kwarg",
    [
        (category_service, "get_category"),
        (customer_service, "get_customer"),
        (supplier_service, "get_supplier"),
    ],
)
def test_get_missing_row_returns_404(db_session, service, id_kwarg):
    with pytest.raises(HTTPException) as exc_info:
        getattr(service, id_kwarg)(db_session, 999999)
    assert exc_info.value.status_code == 404
