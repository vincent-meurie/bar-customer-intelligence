"""Unit tests for transaction model."""
import pytest
from datetime import datetime
from decimal import Decimal

from rest_framework.templatetags.rest_framework import items

from src.core.models import Transaction

class TestTransactionModel:
    """Test suite for transaction model."""

    def test_transaction_creation(self):
        """Test creating a basic transaction."""
        transaction = Transaction(
            transaction_id="TXN001",
            customer_id="CUST001",
            transaction_date=datetime(2024, 10, 15, 19, 30),
            items=[
                {"name": "Negroni", "quantity": 2, "unit_price": Decimal("12.50")},
                {"name": "Nachos", "quantity": 1, "unit_price": Decimal("8.00")},
            ],
            payment_method="card"
        )

        assert transaction.transaction_id == "TXN001"
        assert transaction.customer_id == "CUST001"
        assert transaction.payment_method == "card"
        assert len(transaction.items) == 2

    def test_transaction_total_amount_calculation(self):
        """Test automatic calculation of total amount."""
        transaction = Transaction(
            transaction_id="TXN002",
            customer_id="CUST001",
            transaction_date=datetime(2024, 10, 15, 20, 00),
            items=[
                {"name": "Beer", "quantity": 3, "unit_price": Decimal("6.00")},
                {"name": "Wings", "quantity": 1, "unit_price": Decimal("12.00")},
            ],
            payment_method="cash",
        )

        assert transaction.total_amount == Decimal("30.00")

    def test_transaction_with_single_item(self):
        """Test transaction with single item."""
        transaction = Transaction(
            transaction_id="TXN003",
            customer_id="CUST002",
            transaction_date=datetime.now(),
            items=[
                {"name": "Whiskey", "quantity": 1, "unit_price": Decimal("15.00")},
            ],
            payment_method="card",
        )

        assert transaction.total_amount == Decimal("15.00")
        assert transaction.item_count == 1

    def test_transaction_validation_missing_id(self):
        """Test transaction with missing id raises error."""
        with pytest.raises(ValueError, match="transaction_id is required"):
            Transaction(
                customer_id="CUST001",
                transaction_date=datetime.now(),
                items=[],
                payment_method="cash",
            )

    def test_transaction_validation_missing_customer_id(self):
        """Test transaction with missing customer_id raises error."""
        with pytest.raises(ValueError, match="customer_id is required"):
            Transaction(
                transaction_id="TXN004",
                transaction_date=datetime.now(),
                items=[],
                payment_method="cash",
            )

    def test_transaction_validation_empty_items(self):
        """Test transaction with empty items raises error."""
        with pytest.raises(ValueError, match="Transaction must have at least one item"):
            Transaction(
                transaction_id="TXN005",
                customer_id="CUST001",
                transaction_date=datetime.now(),
                items=[],
                payment_method="cash",
            )

    def test_transaction_invalid_payment_method(self):
        """Test transaction with invalid payment_method raises error."""
        with pytest.raises(ValueError, match="Invalid payment method"):
            Transaction(
                transaction_id="TXN006",
                customer_id="CUST001",
                transaction_date=datetime.now(),
                items=[
                    {"name": "Beer", "quantity": 1, "unit_price": Decimal("6.00")},
                ],
                payment_method="cryptocurrency",
            )

    def test_transaction_item_count(self):
        """Test transaction item count calculation."""
        transaction = Transaction(
            transaction_id="TXN007",
            customer_id="CUST001",
            transaction_date=datetime.now(),
            items=[
                {"name": "Beer", "quantity": 3, "unit_price": Decimal("6.00")},
                {"name": "Cocktails", "quantity": 2, "unit_price": Decimal("10.00")},
                {"name": "Snacks", "quantity": 1, "unit_price": Decimal("5.00")},
            ],
            payment_method="card",
        )

        assert transaction.item_count == 6

    def test_transaction_with_tip(self):
        """Test transaction with tip."""
        transaction = Transaction(
            transaction_id="TXN008",
            customer_id="CUST001",
            transaction_date=datetime.now(),
            items=[
                {"name": "Martini", "quantity": 1, "unit_price": Decimal("14.00")}
            ],
            payment_method="card",
            tip_amount=Decimal("3.00"),
        )

        assert transaction.tip_amount == Decimal("3.00")
        assert transaction.total_with_tip == Decimal("17.00")

    def test_transaction_repr(self):
        """Test transaction repr."""
        transaction = Transaction(
            transaction_id="TXN009",
            customer_id="CUST001",
            transaction_date=datetime(2024, 10, 15),
            items=[{"name": "Beer", "quantity": 1, "unit_price": Decimal("6.00")}],
            payment_method="cash",
        )

        assert "TXN009" in repr(transaction)
        assert "CUST001" in repr(transaction)