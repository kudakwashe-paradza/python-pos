
from decimal import Decimal

from fastapi import HTTPException
import pytest

from models.user import User
from schemas.product import ProductCreate, ProductUpdate
from schemas.inventory import InventoryCreate
from schemas.sale import SaleCreate, SaleUpdate
from schemas.sale_item import SaleItemCreate, SaleItemUpdate
from schemas.payment import PaymentCreate, PaymentUpdate
from schemas.receipt import ReceiptCreate, ReceiptUpdate
from schemas.user import UserCreate, UserUpdate
from services import (
    product_service,
    inventory_service,
    sale_service,
    sale_item_service,
    payment_service,
    receipt_service,
    user_service,
)


@pytest.fixture()
def user(db_session):
    u = User(
        employee_code="EMP-CRUD",
        user_name="crud_user",
        role="cashier",
        password_hash="irrelevant",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture()
def product(db_session):
    return product_service.create_product(
        db_session,
        ProductCreate(
            product_name="Vitamin C 500mg",
            barcode="1112223334445",
            unit_price=Decimal("4.00"),
            stock_quantity=20,
        ),
    )


@pytest.fixture()
def sale(db_session, user):
    return sale_service.create_sale(
        db_session, SaleCreate(user_id=user.id, total_amount=Decimal("8.00"))
    )


def test_product_update_and_delete(db_session, product):
    updated = product_service.update_product(
        db_session, product.id, ProductUpdate(unit_price=Decimal("4.50"), stock_quantity=15)
    )
    assert updated.unit_price == Decimal("4.50")
    assert updated.stock_quantity == 15

    product_service.delete_product(db_session, product.id)
    with pytest.raises(HTTPException) as exc_info:
        product_service.get_product(db_session, product.id)
    assert exc_info.value.status_code == 404


def test_inventory_delete(db_session, product):
    batch = inventory_service.create_inventory(
        db_session, InventoryCreate(product_id=product.id, quantity=50)
    )
    inventory_service.delete_inventory(db_session, batch.id)
    with pytest.raises(HTTPException) as exc_info:
        inventory_service.get_inventory(db_session, batch.id)
    assert exc_info.value.status_code == 404


def test_sale_update_and_delete(db_session, sale):
    updated = sale_service.update_sale(
        db_session, sale.id, SaleUpdate(total_amount=Decimal("9.99"))
    )
    assert updated.total_amount == Decimal("9.99")

    sale_service.delete_sale(db_session, sale.id)
    with pytest.raises(HTTPException) as exc_info:
        sale_service.get_sale(db_session, sale.id)
    assert exc_info.value.status_code == 404


def test_sale_item_update_and_delete(db_session, sale, product):
    item = sale_item_service.create_sale_item(
        db_session,
        SaleItemCreate(
            sale_id=sale.id,
            product_id=product.id,
            quantity_sold=1,
            unit_price_at_sale=Decimal("4.00"),
            sub_total=Decimal("4.00"),
        ),
    )
    updated = sale_item_service.update_sale_item(
        db_session, item.id, SaleItemUpdate(quantity_sold=2, sub_total=Decimal("8.00"))
    )
    assert updated.quantity_sold == 2
    assert updated.sub_total == Decimal("8.00")

    sale_item_service.delete_sale_item(db_session, item.id)
    with pytest.raises(HTTPException) as exc_info:
        sale_item_service.get_sale_item(db_session, item.id)
    assert exc_info.value.status_code == 404


def test_payment_update_and_delete(db_session, sale):
    payment = payment_service.create_payment(
        db_session,
        PaymentCreate(sale_id=sale.id, payment_method="cash", payment_status=False),
    )
    updated = payment_service.update_payment(
        db_session, payment.id, PaymentUpdate(payment_status=True)
    )
    assert updated.payment_status is True

    payment_service.delete_payment(db_session, payment.id)
    with pytest.raises(HTTPException) as exc_info:
        payment_service.get_payment(db_session, payment.id)
    assert exc_info.value.status_code == 404


def test_receipt_update_and_delete(db_session, sale):
    receipt = receipt_service.create_receipt(
        db_session, ReceiptCreate(sale_id=sale.id, receipt_number="RCPT-CRUD-1")
    )
    updated = receipt_service.update_receipt(
        db_session, receipt.id, ReceiptUpdate(is_voided=True)
    )
    assert updated.is_voided is True

    receipt_service.delete_receipt(db_session, receipt.id)
    with pytest.raises(HTTPException) as exc_info:
        receipt_service.get_receipt(db_session, receipt.id)
    assert exc_info.value.status_code == 404


def test_user_update_and_delete(db_session):
    created = user_service.create_user(
        db_session,
        UserCreate(
            employee_code="EMP-USERCRUD",
            user_name="user_crud_target",
            role="cashier",
            password="whatever-secure",
        ),
    )
    updated = user_service.update_user(db_session, created.id, UserUpdate(role="manager"))
    assert updated.role == "manager"

    user_service.delete_user(db_session, created.id)
    with pytest.raises(HTTPException) as exc_info:
        user_service.get_user(db_session, created.id)
    assert exc_info.value.status_code == 404
