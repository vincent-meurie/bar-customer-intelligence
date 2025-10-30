"""
Synthetic data generation for bar/izakaya customer and transaction data.
Realistic data for Bangkok entertainment venue scenario.
"""

from dataclasses import asdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
import random
import csv
import json

from faker import Faker
from core.models import Customer, Transaction

# Initialize Faker with Thai locale for more realistic Bangkok names
fake = Faker(['en_US', 'th_TH'])

# Bangkok Bar/Izakaya Menu Items (prices in THB)
MENU_ITEMS = [
    # Drinks - Beer
    {"name": "Singha Beer", "category": "beer", "price": Decimal("80"), "popularity": 0.25},
    {"name": "Chang Beer", "category": "beer", "price": Decimal("70"), "popularity": 0.20},
    {"name": "Leo Beer", "category": "beer", "price": Decimal("75"), "popularity": 0.15},
    {"name": "Asahi Super Dry", "category": "beer", "price": Decimal("120"), "popularity": 0.18},
    {"name": "Sapporo", "category": "beer", "price": Decimal("130"), "popularity": 0.12},

    # Drinks - Sake
    {"name": "House Sake", "category": "sake", "price": Decimal("150"), "popularity": 0.15},
    {"name": "Premium Sake", "category": "sake", "price": Decimal("280"), "popularity": 0.08},
    {"name": "Sake Flight", "category": "sake", "price": Decimal("320"), "popularity": 0.05},

    # Drinks - Cocktails
    {"name": "Negroni", "category": "cocktail", "price": Decimal("320"), "popularity": 0.12},
    {"name": "Old Fashioned", "category": "cocktail", "price": Decimal("280"), "popularity": 0.10},
    {"name": "Lychee Martini", "category": "cocktail", "price": Decimal("220"), "popularity": 0.09},
    {"name": "Long Island", "category": "cocktail", "price": Decimal("340"), "popularity": 0.08},

    # Drinks - Whiskey/Spirits
    {"name": "Whiskey Soda", "category": "spirits", "price": Decimal("180"), "popularity": 0.10},
    {"name": "Gin & Tonic", "category": "spirits", "price": Decimal("170"), "popularity": 0.11},

    # Food - Izakaya Style
    {"name": "Edamame", "category": "appetizer", "price": Decimal("80"), "popularity": 0.20},
    {"name": "Gyoza", "category": "appetizer", "price": Decimal("120"), "popularity": 0.18},
    {"name": "Karaage", "category": "appetizer", "price": Decimal("150"), "popularity": 0.16},
    {"name": "Yakitori Skewers", "category": "appetizer", "price": Decimal("140"), "popularity": 0.15},
    {"name": "Takoyaki", "category": "appetizer", "price": Decimal("130"), "popularity": 0.12},
    {"name": "Agedashi Tofu", "category": "appetizer", "price": Decimal("110"), "popularity": 0.10},

    # Food - Mains
    {"name": "Ramen Bowl", "category": "main", "price": Decimal("180"), "popularity": 0.14},
    {"name": "Okonomiyaki", "category": "main", "price": Decimal("200"), "popularity": 0.11},
    {"name": "Tonkatsu", "category": "main", "price": Decimal("220"), "popularity": 0.10},

    # Snacks
    {"name": "Nuts Mix", "category": "snack", "price": Decimal("60"), "popularity": 0.08},
    {"name": "Crispy Squid", "category": "snack", "price": Decimal("100"), "popularity": 0.09},
]

class CustomerGenerator:
    """Generate synthetic customer data."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize the customer generator."""
        if seed:
            Faker.seed(seed)
            random.seed(seed)

    def generate_customer(self, customer_id: str) -> Customer:
        """
        Generate a single customer.

        Args:
            customer_id (str): Unique customer identifier.

        Returns:
            Customer object
        """
        # Generate age (legal drinking age in Thailand is 20, but we'll use 21-65)
        age = random.choices(
            population=[21, 25, 30, 35, 40, 45, 50, 55, 60, 65],
            weights=[5, 20, 25, 20, 15, 8, 4, 2, 0.5, 0.5], # Most customers 25-40
            k=1
        )[0]

        date_of_birth = datetime.now() - timedelta(days=age * 365)

        # Registration date (within last 2 years)
        registration_date = fake.date_time_between(start_date='-2y', end_date='now')

        # Mix of Thai and expat names
        if random.random() < 0.3: # 30% expat customers
            first_name = fake.first_name()
            last_name = fake.last_name()
        else: # 70% Thai customers
            first_name = fake.first_name_nonbinary() # More neutral names
            last_name = fake.last_name()

        # sanitize names for email
        def sanitize_for_email(name: str) -> str:
            """Remove non-alphanumeric characters"""
            import re
            # Keep only alphanumeric characters
            sanitized = re.sub(r'[^a-zA-Z0-9]', '', name)
            return sanitized.lower() if sanitized else 'user'

        email_first = sanitize_for_email(first_name)
        email_last = sanitize_for_email(last_name)

        # Fallback to generated email if names are too short
        if len(email_first) < 2 or len(email_last) < 2:
            email = fake.email()
        else:
            email = f"{email_first}.{email_last}@{fake.free_email_domain()}"

        customer = Customer(
            customer_id=customer_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=fake.phone_number()[:15],
            date_of_birth=date_of_birth,
            registration_date=registration_date,
            city="Bangkok",
            country="Thailand",
            marketing_opt_in=random.choice([True, False]),
        )

        return customer

    def generate_customers(self, count: int) -> List[Customer]:
        """
        Generate a list of customers.

        Args:
            count (int): Number of customers to generate.

        Returns:
            List of Customer objects
        """
        customers = []
        for i in range(count):
            customer_id = f"CUST{i+1:05d}"
            customers.append(self.generate_customer(customer_id))

        return customers

class TransactionGenerator:
    """Generate synthetic transaction data."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize the transaction generator."""
        if seed:
            random.seed(seed)

    def _select_menu_items(self) -> List[Dict[str, Any]]:
        """
        Select items for a transaction based on popularity.

        Returns:
            List of item dictionaries with name, quantity and unit_price.
        """
        # Decide how many items (1-5, weighted toward 2-3)
        num_items = random.choices(
            population=[1, 2, 3, 4, 5],
            weights=[15, 35, 30, 15, 5],
            k=1
        )[0]

        # Select items based on popularity
        selected_items = []
        available_items = MENU_ITEMS.copy()

        for _ in range(num_items):
            if not available_items:
                break

            # Weight selection by popularity
            weights = [item["popularity"] for item in available_items]
            item = random.choices(available_items, weights=weights, k=1)[0]

            # Determine quantity (1-3 for drinks, 1-2 for food)
            if item["category"] in ["beer", "sake", "cocktail", "spirits"]:
                quantity = random.choices([1, 2, 3], weights=[50, 35, 15], k=1)[0]
            else:
                quantity = random.choices([1, 2], weights=[70, 30], k=1)[0]

            selected_items.append({
                "name": item["name"],
                "quantity": quantity,
                "unit_price": item["price"],
            })

            # Remove items to avoid duplicates
            available_items.remove(item)

        return selected_items

    def generate_transaction(
            self,
            transaction_id: str,
            customer_id: str,
            transaction_date: Optional[datetime] = None,
        ) -> Transaction:
        """
        Generate a single transaction.

        Args:
            transaction_id (str): Unique transaction identifier.
            customer_id (str): Unique customer identifier.
            transaction_date (datetime, optional): Date of transaction (defaults to now).

        Returns:
            Transaction object
        """
        if transaction_date is None:
            transaction_date = datetime.now()

        items = self._select_menu_items()

        # Payment method (mobile popular in Bangkok)
        payment_method = random.choices(
            population=["cash", "card", "mobile", "tab"],
            weights=[20, 35, 40, 5],
            k=1
        )[0]

        # Tip (not as common in Thailand, but some customers do)
        # Calculate total first
        total = sum(Decimal(str(item["quantity"])) * item["unit_price"] for item in items)

        # 20% chance of tip, usually 10-51% of bill
        if random.random() < 0.2:
            tip_percentage = random.uniform(0.10, 0.15)
            tip_amount = (total * Decimal(str(tip_percentage))).quantize(Decimal("0.01"))
        else:
            tip_amount = Decimal("0.00")

        transaction = Transaction(
            transaction_id=transaction_id,
            customer_id=customer_id,
            transaction_date=transaction_date,
            items=items,
            payment_method=payment_method,
            tip_amount=tip_amount,
        )

        return transaction

class BarDataGenerator:
    """Generate complete bar/izakaya datasets with realistic patterns."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize the bar data generator."""
        self.seed = seed
        self.customer_gen = CustomerGenerator(seed=seed)
        self.transaction_gen = TransactionGenerator(seed=seed)

        if seed:
            random.seed(seed)

    def _assign_customer_behavior(self, num_customers: int) -> Dict[str, str]:
        """
        Assign customer behavior for each customer.

        Args:
            num_customers (int): Number of customers to generate.

        Returns:
            Dictionary mapping customer_id to behavior type
        """
        behaviors = {
            "champion": 0.15,
            "loyal": 0.20,
            "potential": 0.15,
            "new": 0.20,
            "at_risk": 0.10,
            "lost": 0.10,
            "hibernating": 0.10,
        }

        customer_behaviors = {}
        for i in range(num_customers):
            customer_id = f"CUST{i+1:05d}"
            behavior = random.choices(
                population=list(behaviors.keys()),
                weights=list(behaviors.values()),
                k=1
            )[0]
            customer_behaviors[customer_id] = behavior

        return customer_behaviors

    def _safe_randint(self, min_val: int, max_val: int) -> int:
        """
        Safe random integer that handles invalid ranges.

        Args:
            min_val (int): Minimum integer value.
            max_val (int): Maximum integer value.

        Returns:
            Random integer or min_val is range is invalid
        """
        if min_val > max_val:
            return min_val
        if min_val == max_val:
            return min_val
        return random.randint(min_val, max_val)

    def generate_dataset(
            self,
            num_customers: int = 100,
            num_transactions: int = 500,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
    ) -> Dict[str, List]:
        """
        Generate a complete dataset with customers and transactions.

        Args:
            num_customers (int): Number of customers to generate.
            num_transactions (int): Number of transactions to generate.
            start_date (datetime, optional): Date to start generating (defaults to None).
            end_date (datetime, optional): Date to end generating (defaults to None).

        Returns:
            Dictionary with 'customers' and 'transactions' lists
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()

        # Calculate total days in range
        total_days = max((end_date - start_date).days, 1)

        # Generate customers
        customers = self.customer_gen.generate_customers(num_customers)

        # Assign behavior patterns
        customer_behaviors = self._assign_customer_behavior(num_customers)

        # Generate transactions based on behavior patterns
        transactions = []
        transaction_count = 0

        for customer in customers:
            behavior = customer_behaviors[customer.customer_id]

            # Determine transaction count based on behavior
            if behavior == "champion":
                num_txns = random.randint(15, 30)
                ideal_recency = self._safe_randint(1, 7)
            elif behavior == "loyal":
                num_txns = random.randint(10, 20)
                ideal_recency = self._safe_randint(7, 30)
            elif behavior == "potential":
                num_txns = random.randint(5, 10)
                ideal_recency = self._safe_randint(1, 14)
            elif behavior == "new":
                num_txns = random.randint(1, 3)
                ideal_recency = self._safe_randint(1, 30)
            elif behavior == "at_risk":
                num_txns = random.randint(8, 15)
                ideal_recency = self._safe_randint(60, 120)
            elif behavior == "lost":
                num_txns = random.randint(3, 8)
                ideal_recency = self._safe_randint(150, 300)
            else: # hibernating
                num_txns = random.randint(2, 5)
                ideal_recency = self._safe_randint(120, 200)

            # Cap recency to total days available
            recency_days = min(ideal_recency, total_days)

            # Generate transactions for this customer
            for i in range(num_txns):
                if transaction_count >= num_transactions:
                    break

                # Generate transaction date
                # Most recent transaction is 'recency_days' ago
                # Earlier transactions spread over the date range
                if i == 0: # Most recent
                    days_ago = recency_days
                else:
                    # Distribute other transactions over time
                    # Ensure we don't go beyond the date
                    min_days_ago = min(recency_days + 1, total_days)
                    max_days_ago = total_days
                    days_ago = self._safe_randint(min_days_ago, max_days_ago)

                txn_date = end_date - timedelta(days=days_ago)

                # Ensure date is within range
                if txn_date < start_date:
                    txn_date = start_date
                elif txn_date > end_date:
                    txn_date = end_date

                transaction_id = f"TXN{transaction_count+1:06d}"
                transaction = self.transaction_gen.generate_transaction(
                    transaction_id=transaction_id,
                    customer_id=customer.customer_id,
                    transaction_date=txn_date,
                )

                transactions.append(transaction)
                transaction_count += 1

            if transaction_count >= num_transactions:
                break

        return {
            "customers": customers,
            "transactions": transactions,
        }

    def save_dataset(
            self,
            dataset: Dict[str, List],
            output_dir: str = "data/processed",
    ) -> None:
        """
        Save the dataset to CSV files

        Args:
             dataset: Dataset dictionary with customers and transactions
             output_dir: Directory to save files
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Save customers to CSV
        customers_file = os.path.join(output_dir, "customers.csv")
        with open(customers_file, "w", newline='', encoding='utf-8') as f:
            if dataset["customers"]:
                fieldnames = [
                    "customer_id",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "date_of_birth",
                    "registration_date",
                    "city",
                    "country",
                    "marketing_opt_in"
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for customer in dataset["customers"]:
                    row = {
                        "customer_id": customer.customer_id,
                        "first_name": customer.first_name,
                        "last_name": customer.last_name,
                        "email": customer.email,
                        "phone": customer.phone,
                        "date_of_birth": customer.date_of_birth,
                        "registration_date": customer.registration_date,
                        "city": customer.city,
                        "country": customer.country,
                        "marketing_opt_in": customer.marketing_opt_in
                    }
                    writer.writerow(row)

        # Save transactions to CSV
        transactions_file = os.path.join(output_dir, "transactions.csv")
        with open(transactions_file, "w", newline='', encoding='utf-8') as f:
            if dataset["transactions"]:
                fieldnames = [
                    "transaction_id", "customer_id", "transaction_date",
                    "items", "total_amount", "payment_method", "tip_amount"
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for txn in dataset["transactions"]:
                    row = {
                        "transaction_id": txn.transaction_id,
                        "customer_id": txn.customer_id,
                        "transaction_date": txn.transaction_date,
                        "items": json.dumps([
                            {
                                'name': item['name'],
                                'quantity': item['quantity'],
                                'unit_price': str(item['unit_price']),
                            }
                            for item in txn.items
                        ]),
                        "total_amount": str(txn.total_amount),
                        "payment_method": txn.payment_method,
                        "tip_amount": str(txn.tip_amount),
                    }
                    writer.writerow(row)

        print(f"Dataset saved to {output_dir}")
        print(f"  - {len(dataset['customers'])} customers")
        print(f"  - {len(dataset['transactions'])} transactions")

    def load_dataset(self, data_dir: str = "data/processed") -> Dict[str, List]:
        """
        Load the dataset from CSV files

        Args:
            data_dir (str): Directory to load the dataset from

        Returns:
            Dataset dictionary
        """
        import os

        # Load customers
        customers = []
        customers_file = os.path.join(data_dir, "customers.csv")
        with open(customers_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer = Customer(
                    customer_id=row["customer_id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    email=row["email"],
                    phone=row["phone"],
                    date_of_birth=datetime.fromisoformat(row["date_of_birth"]) if row["date_of_birth"] else None,
                    registration_date=datetime.fromisoformat(row["registration_date"]),
                    city=row["city"],
                    country=row["country"],
                    marketing_opt_in=row["marketing_opt_in"]
                )
                customers.append(customer)

        # Load transactions
        transactions = []
        transactions_file = os.path.join(data_dir, "transactions.csv")
        with open(transactions_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                items = json.loads(row["items"])
                # Convert string prices back to Decimal
                for item in items:
                    item["unit_price"] = Decimal(item["unit_price"])

                transaction = Transaction(
                    transaction_id=row["transaction_id"],
                    customer_id=row["customer_id"],
                    transaction_date=datetime.fromisoformat(row["transaction_date"]),
                    items=items,
                    payment_method=row["payment_method"],
                    tip_amount=Decimal(row["tip_amount"]),
                )
                transactions.append(transaction)

        return {
            "customers": customers,
            "transactions": transactions
        }