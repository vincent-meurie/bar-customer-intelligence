"""
Pytest configuration and fixtures
"""
import pytest
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker
fake = Faker()

@pytest.fixture
def sample_customer_data():
    """Fixture for sample customer data."""
    return {
        'customer_id': 'CUST001',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890',
        'registration_date': datetime(2024, 1, 15),
        'date_of_birth': datetime(1990, 5, 15),
    }

@pytest.fixture
def sample_customer_list():
    """Fixture providing sample customer list."""
    customers = []
    for i in range(10):
        customers.append({
            'customer_id': f'CUST{i:03d}',
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'registration_date': fake.date_time_between(start_date='-2y', end_date='now'),
            'date_of_birth': fake.date_of_birth(minimum_age=21, maximum_age=65),
        })
    return customers