"""Core business models for customer data."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import re

@dataclass
class Customer:
    """Represents a bar/venue customer."""

    customer_id: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    registration_date: datetime = field(default_factory=datetime.now)
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    preferred_contact: str = "email"
    marketing_opt_in: bool = False

    def __post_init__(self):
        """Validates customer data after initialization."""
        if not self.customer_id:
            raise ValueError("customer_id is required")

        if self.email and not self._is_valid_email(self.email):
            raise ValueError("Invalid email format")

    @property
    def full_name(self) -> str:
        """Returns customer full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> Optional[int]:
        """Calculates customer age from date of birth."""
        if not self.date_of_birth:
            return None

        today = datetime.now()
        age = today.year - self.date_of_birth.year

        # adjust if birthday hasn't occurred this year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1

        return age

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validates customer email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def __repr__(self) -> str:
        return f"Customer(id={self.customer_id}, name={self.full_name})"