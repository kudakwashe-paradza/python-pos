"""
Exercises the services that depend on other rows existing first:
Product -> Inventory, and User -> Sale -> (SaleItem, Payment, Receipt).

User rows are inserted directly through the model rather than through
user_service.create_user/auth_service.register, since both of those are
covered (and shown broken) in test_auth_and_user_service.py. This lets
the sale/payment/receipt chain be tested independently of that bug.
"""
from decimal import Decimal

from models.user import User
from schemas.product import ProductCreate
from schemas.inventory import InventoryCreate, InventoryUpdate
from schemas.sale import SaleCreate
from schemas.sale_item import SaleItemCreate
from schemas.payment import PaymentCreate
from schemas.receipt import ReceiptCreate
from services import (
    product_service,
    inventory_service,
    sale_service,
    sale_item_service,
    payment_service,
    receipt_service,
)


def make_user(db_session, user_name="cashier1"):
    user = User(
        employee_code=f"EMP-{user_name}",
        user_name=user_name,
        role="cashier",
        password_hash="irrelevant-for-this-test",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_inventory_receipt_added_against_a_product(db_session):
    product = product_service.create_product(
        db_session,
        ProductCreate(
            product_name="Amoxicillin 250mg",
            barcode="9990001112223",
            unit_price=Decimal("12.50"),
            stock_quantity=0,
        ),
    )

    batch = inventory_service.create_inventory(
        db_session,
        InventoryCreate(product_id=product.id, batch_number="B-001", quantity=100),
    )
    assert batch.product_id == product.id
    assert batch.quantity == 100

    updated_batch = inventory_service.update_inventory(
        db_session, batch.id, InventoryUpdate(quantity=80)
    )
    assert updated_batch.quantity == 80


def test_full_sale_flow_creates_items_payment_and_receipt(db_session):
    user = make_user(db_session)
    product = product_service.create_product(
        db_session,
        ProductCreate(
            product_name="Ibuprofen 200mg",
            barcode="5550001112223",
            unit_price=Decimal("3.00"),
            stock_quantity=50,
        ),
    )

    sale = sale_service.create_sale(
        db_session,
        SaleCreate(user_id=user.id, total_amount=Decimal("6.00")),
    )
    assert sale.id is not None

    sale_item = sale_item_service.create_sale_item(
        db_session,
        SaleItemCreate(
            sale_id=sale.id,
            product_id=product.id,
            quantity_sold=2,
            unit_price_at_sale=Decimal("3.00"),
            sub_total=Decimal("6.00"),
        ),
    )
    assert sale_item.sale_id == sale.id

    payment = payment_service.create_payment(
        db_session,
        PaymentCreate(sale_id=sale.id, payment_method="cash", payment_status=True),
    )
    assert payment.sale_id == sale.id

    receipt = receipt_service.create_receipt(
        db_session,
        ReceiptCreate(sale_id=sale.id, receipt_number="RCPT-0001"),
    )
    assert receipt.sale_id == sale.id


    unchanged_product = product_service.get_product(db_session, product.id)
    assert unchanged_product.stock_quantity == 50
