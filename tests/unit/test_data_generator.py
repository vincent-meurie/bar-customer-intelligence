"""Unit tests for synthetic data generation."""
from itertools import count

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from analytics.data_generator import (
    CustomerGenerator,
    TransactionGenerator,
    BarDataGenerator,
    MENU_ITEMS,
)

class TestCustomerGenerator:
    """Test customer data generation."""

    def test_generate_single_customer(self):
        """Test generating a single customer."""
        generator = CustomerGenerator()
        customer = generator.generate_customer(customer_id="CUST001")

        assert customer.customer_id == "CUST001"
        assert customer.first_name
        assert customer.last_name
        assert customer.email
        assert "@" in customer.email
        assert customer.age >= 21
        assert customer.age <= 65

    def test_generate_multiple_customers(self):
        """Test generating multiple customers."""
        generator = CustomerGenerator()
        customers = generator.generate_customers(count=50)

        assert len(customers) == 50
        # Check unique IDs
        customer_ids = [c.customer_id for c in customers]
        assert len(customer_ids) == len(set(customer_ids))

    def test_customer_age_distribution(self):
        """Test that customer ages follow realistic distribution."""
        generator = CustomerGenerator()
        customers = generator.generate_customers(count=100)

        ages = [c.age for c in customers if c.age]
        avg_age = sum(ages) / len(ages)

        # Average age should be reasonable for bar customers (25 - 40)
        assert 25 <= avg_age <= 40

class TestTransactionGenerator:
    """Test transaction data generation."""

    def test_generate_single_transaction(self):
        """Test generating a single transaction."""
        generator = TransactionGenerator()
        transaction = generator.generate_transaction(
            transaction_id="TX001",
            customer_id="CUST001",
        )

        assert transaction.customer_id == "CUST001"
        assert transaction.transaction_id == "TX001"
        assert len(transaction.items) > 0
        assert transaction.total_amount > 0
        assert transaction.payment_method in ["cash", "card", "mobile", "tab"]

    def test_transaction_items_from_menu(self):
        """Test that transaction items are generated from menu."""
        generator = TransactionGenerator()
        transaction = generator.generate_transaction(
            transaction_id="TX001",
            customer_id="CUST001",
        )

        for item in transaction.items:
            item_name = item.get("name")
            assert any(menu_item["name"] == item_name for menu_item in MENU_ITEMS)

    def test_transaction_realistic_quantity(self):
        """Test that item quantities are realistic."""
        generator = TransactionGenerator()
        transaction = generator.generate_transaction(
            transaction_id="TX001",
            customer_id="CUST001",
        )

        for item in transaction.items:
            quantity = item.get("quantity", 0)
            assert 1 <= quantity <= 10 # Realistic order quantities

class TestBarDataGenerator:
    """Test complete bar data generation."""

    def test_generate_dataset(self):
        """Test generating a complete bar dataset."""
        generator = BarDataGenerator()
        dataset = generator.generate_dataset(
            num_customers=20,
            num_transactions=100,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
        )

        assert "customers" in dataset
        assert "transactions" in dataset
        assert len(dataset["customers"]) == 20
        assert len(dataset["transactions"]) == 100

    def test_transactions_within_date_range(self):
        """Test that transactions are within specified date range."""
        generator = BarDataGenerator()
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 6, 30)

        dataset = generator.generate_dataset(
            num_customers=10,
            num_transactions=50,
            start_date=start_date,
            end_date=end_date,
        )

        for txn in dataset["transactions"]:
            assert start_date <= txn.transaction_date <= end_date

    def test_customer_behavior_patterns(self):
        """Test that customers have realistic transaction patterns."""
        generator = BarDataGenerator()
        dataset = generator.generate_dataset(
            num_customers=10,
            num_transactions=100,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
        )

        # Count transactions per customer
        customer_txn_count = {}
        for txn in dataset["transactions"]:
            customer_id = txn.customer_id
            customer_txn_count[customer_id] = customer_txn_count.get(customer_id, 0) + 1

        # Some customers should be frequent, some infrequent
        assert max(customer_txn_count.values()) > min(customer_txn_count.values())

    def test_save_and_load_data(self, tmp_path):
        """Test saving and loading dataset to/from files."""
        generator = BarDataGenerator()
        dataset = generator.generate_dataset(
            num_customers=5,
            num_transactions=20,
        )

        # Save to temporary directory
        output_dir = tmp_path / "data"
        generator.save_dataset(dataset, output_dir=str(output_dir))

        # Verify files exist
        assert (output_dir / "customers.csv").exists()
        assert (output_dir / "transactions.csv").exists()

        # Load and verify
        loaded_dataset = generator.load_dataset(data_dir=str(output_dir))
        assert len(loaded_dataset["customers"]) == 5
        assert len(loaded_dataset["transactions"]) == 20

class TestMenuItems:
    """Test menu item data."""

    def test_menu_items_exist(self):
        """Test that menu items are defined."""
        assert len(MENU_ITEMS) > 0

    def test_menu_items_structure(self):
        """Test that menu items have required fields."""
        for item in MENU_ITEMS:
            assert "name" in item
            assert "category" in item
            assert "price" in item
            assert "popularity" in item

    def test_menu_prices_realistic(self):
        """Test that menu prices are realistic for Bangkok."""
        for item in MENU_ITEMS:
            price = float(item["price"])
            assert 50 <= price <= 500