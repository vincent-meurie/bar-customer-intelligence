"""Core business models for customer data."""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, ClassVar
import re

@dataclass
class Customer:
    """Represents a bar/venue customer."""

    EMAIL_PATTERN: ClassVar[str] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

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

@dataclass
class Transaction:
    """Represents a purchase transaction."""

    # Valid payment methods
    VALID_PAYMENT_METHODS: ClassVar[List[str]] = ["cash", "card", "mobile", "tab"]

    transaction_id: Optional[str] = None
    customer_id: Optional[str] = None
    transaction_date: Optional[datetime] = None
    items: List[Dict[str, Any]] = field(default_factory=list)
    payment_method: str = "cash"
    tip_amount: Decimal = Decimal("0.00")
    discount_amount: Decimal = Decimal("0.00")
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        """Validates transaction data after initialization."""
        self._validate_required_fields()
        self._validate_items()
        self._validate_payment_method()

    def _validate_required_fields(self) -> None:
        """Validate that required fields are present."""
        if not self.transaction_id:
            raise ValueError("transaction_id is required")
        if not self.customer_id:
            raise ValueError("customer_id is required")
        if not self.transaction_date:
            raise ValueError("transaction_date is required")

    def _validate_items(self) -> None:
        """Validate that transaction has items."""
        if not self.items or len(self.items) == 0:
            raise ValueError("Transaction must have at least one item")

    def _validate_payment_method(self) -> None:
        """Validate that payment method is valid."""
        if self.payment_method not in self.VALID_PAYMENT_METHODS:
            raise ValueError(
                f"Invalid payment method. Must be one of: {', '.join(self.VALID_PAYMENT_METHODS)}"
            )

    @property
    def total_amount(self) -> Decimal:
        """Calculates total amount from items."""
        total = Decimal("0.00")
        for item in self.items:
            quantity = Decimal(str(item.get("quantity", 0)))
            unit_price = Decimal(str(item.get("unit_price", 0)))
            total += quantity * unit_price
        return total

    @property
    def total_with_tip(self) -> Decimal:
        """Calculate total including tip."""
        return self.total_amount + self.tip_amount

    @property
    def item_count(self) -> int:
        """Calculate total number of items (sum of quantities)."""
        return sum(item.get("quantity", 0) for item in self.items)

    def __repr__(self) -> str:
        return f"Transaction(id={self.transaction_id}, customer_id={self.customer_id}, total={self.total_amount})"