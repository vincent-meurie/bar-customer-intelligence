import pytest
from datetime import datetime, timedelta
from src.core.models import Customer

class TestCustomerModel:
    """Test suite for Customer model."""

    def test_customer_creation(self):
        """Test creating a basic customer."""
        customer = Customer(
            customer_id="CUST001",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            registration_date=datetime(2024, 1, 15),
        )

        assert customer.customer_id == "CUST001"
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.email == "john.doe@example.com"
        assert customer.full_name == "John Doe"

    def test_customer_age_calculation(self):
        """Test age calculation from date of birth."""
        dob = datetime.now() - timedelta(days=365 * 30) # 30 years ago
        customer = Customer(
            customer_id="CUST002",
            first_name="Jane",
            last_name="Smith",
            date_of_birth=dob,
        )

        assert customer.age == 30

    def test_customer_without_dob(self):
        """Test customer without date of birth."""
        customer = Customer(
            customer_id="CUST003",
            first_name="Bob",
            last_name="Wilson",
        )

        assert customer.age is None

    def test_customer_validation_invalid_email(self):
        """Test customer with invalid email raises error."""
        with pytest.raises(ValueError, match="Invalid email"):
            Customer(
                customer_id="CUST004",
                first_name="Invalid",
                last_name="Email",
                email="not-an-email",
            )

    def test_customer_validation_missing_id(self):
        """Test customer without ID raises error."""
        with pytest.raises(ValueError, match="customer_id is required"):
            Customer(first_name="No", last_name="ID")