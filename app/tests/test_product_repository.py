"""
repositories/product_repository.py

update() has its commit/refresh/return statements indented inside the
for-loop body. On the first field it commits and returns immediately, so
any additional fields passed in `data` are silently dropped.
"""
import pytest
from decimal import Decimal

from models.product import Product
from repositories.product_repository import product_repository


@pytest.fixture()
def seeded_product(db_session):
    product = Product(
        product_name="Paracetamol 500mg",
        barcode="1234567890123",
        unit_price=Decimal("5.00"),
        stock_quantity=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def test_update_applies_a_single_field(db_session, seeded_product):
    updated = product_repository.update(db_session, seeded_product, {"stock_quantity": 25})
    assert updated.stock_quantity == 25


def test_update_applies_multiple_fields_in_one_call(db_session, seeded_product):
    updated = product_repository.update(
        db_session,
        seeded_product,
        {"stock_quantity": 25, "unit_price": Decimal("6.50")},
    )
    assert updated.stock_quantity == 25
    assert updated.unit_price == Decimal("6.50")
