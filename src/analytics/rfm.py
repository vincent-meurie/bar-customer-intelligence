"""
RFM (Recency, Frequency, Monetary) Analysis for customer segmentation
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
import pandas as pd

@dataclass
class RFMScore:
    """Represents RFM score for a customer."""

    customer_id: str
    recency: int # Days since last purchase
    frequency: int # Number of purchases
    monetary: Decimal # Total amount spent
    r_score: int # Recency score (1-5)
    f_score: int # Frequency score (1-5)
    m_score: int #Monetary score (1-5)

    @property
    def rfm_score(self) -> str:
        """Return combined RFM score as a string."""
        return f"{self.r_score}{self.f_score}{self.m_score}"

    @property
    def segment(self) -> str:
        """Determine customer segment based on RFM scores."""
        # Champions: High value customers who bought recently and often
        if self.r_score >= 4 and self.f_score >= 4 and self.m_score >= 4:
            return "Champions"

        # Loyal Customers: Buy often, good monetary value
        elif self.f_score >= 4 and self.m_score >= 3:
            return "Loyal Customers"

        # Potential Loyalists: Recent customers, decent frequency
        elif self. r_score >= 4 and self.f_score >= 2 and self.m_score >= 2:
            return "Potential Loyalists"

        # New Customers: Recent purchase, low frequency
        elif self.r_score >= 4 and self.f_score <= 2:
            return "New Customers"

        # At Risk: Used to be good customers, haven't purchased recently
        elif self.r_score <= 2 and self.f_score >= 3 and self.m_score >= 3:
            return "At Risk"

        # Can't Lose Them: High value customers who haven't purchased recently
        elif self.r_score <= 2 and self.f_score >= 4 and self.m_score >= 4:
            return "Can't Lose Them"

        # Hibernating: Low recency, low frequency, but had some value
        elif self.r_score <= 2 and self.f_score <= 2 and self.m_score >= 2:
            return "Hibernating"

        # Lost: Haven't purchased in a long time, low everything
        elif self.r_score <= 2 and self.f_score <= 2 and self.m_score <= 2:
            return "Lost"

        # About to Sleep: Below average recency, frequency, and monetary
        elif self.r_score <= 3 and self.f_score <= 3:
            return "About to Sleep"

        # Promising: Recent customers with average frequency
        elif self.r_score >= 3 and self.f_score <= 3 and self.m_score <= 3:
            return "Promising"

        # Need Attention: Average across all metrics
        else:
            return "Need Attention"

    def __repr__(self) -> str:
        return f"RFMScore(customer={self.customer_id}, RFM={self.rfm_score}, segment={self.segment})"

class RFMAnalyzer:
    """Analyze customer transactions and calculate RFM scores."""

    def __init__(self, reference_date: Optional[datetime] = None):
        """
        Initialize RFMAnalyzer.

        Args:
            reference_date: Date to calculate recency from (defaults to now)
        """
        self.reference_date = reference_date or datetime.now()

    def calculate_recency(self, customer_id: str, transactions: List[Dict[str, Any]]) -> int:
        """
        Calculate recency (days since last purchase) for a customer.

        Args:
            customer_id: Customer ID
            transactions: List of transaction dictionaries

        Returns:
            Number of days since last purchase
        """
        customer_transactions = [
            t for t in transactions if t.get("customer_id") == customer_id
        ]

        if not customer_transactions:
            return float('inf') # Customer has no transactions

        # Find most recent transaction
        most_recent = max(
            customer_transactions,
            key=lambda t: t.get("transaction_date", datetime.min)
        )

        last_purchase_date = most_recent.get("transaction_date")

        if not last_purchase_date:
            return float('inf')

        # Calculate days difference
        recency = (self.reference_date - last_purchase_date).days

        return recency

    def calculate_frequency(self, customer_id: str, transactions: List[Dict[str, Any]]) -> int:
        """
        Calculate frequency (number of purchases) for a customer.

        Args:
            customer_id: Customer ID
            transactions: List of transaction dictionaries

        Returns:
            Number of purchases
        """
        customer_transactions = [
            t for t in transactions if t.get("customer_id") == customer_id
        ]

        return len(customer_transactions)

    def calculate_monetary(self, customer_id: str, transactions: List[Dict[str, Any]]) -> Decimal:
        """
        Calculate monetary (total spent) for a customer.

        Args:
            customer_id: Customer ID
            transactions: List of transaction dictionaries

        Returns:
            Total amount spent
        """
        customer_transactions = [
            t for t in transactions if t.get("customer_id") == customer_id
        ]

        total = Decimal("0.00")
        for transaction in customer_transactions:
            amount = transaction.get("total_amount", Decimal("0.00"))
            if isinstance(amount, (int, float)):
                amount = Decimal(str(amount))
            total += amount

        return total

    def _calculate_score(self, value: float, quantiles: List[float]) -> int:
        """
        Convert a value to a score (1-5) based on quantiles.

        Args:
            value: Value to score
            quantiles: List of 4 quantiles boundaries

        Returns:
            Score from 1 to 5
        """
        if value <= quantiles[0]:
            return 1
        elif value <= quantiles[1]:
            return 2
        elif value <= quantiles[2]:
            return 3
        elif value <= quantiles[3]:
            return 4
        else:
            return 5

    def calculate_rfm_scores(self, transactions: List[Dict[str, Any]]) -> List[RFMScore]:
        """
        Calculate RFM scores for all customers in the transaction list.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            List of RFMScore objects
        """
        # Get unique customer IDs
        customer_ids = list(set(t.get("customer_id") for t in transactions if t.get("customer_id")))

        if not customer_ids:
            return []

        # Calculate RFM metrics for each customer
        rfm_data = []
        for customer_id in customer_ids:
            recency = self.calculate_recency(customer_id, transactions)
            frequency = self.calculate_frequency(customer_id, transactions)
            monetary = self.calculate_monetary(customer_id, transactions)

            # Skip customers with infinite recency
            if recency == float("inf"):
                continue

            rfm_data.append({
                "customer_id": customer_id,
                "recency": recency,
                "frequency": frequency,
                "monetary": float(monetary),
            })

        if not rfm_data:
            return []

        # Convert to DataFrame for easier quantile calculation
        df = pd.DataFrame(rfm_data)

        # Calculate quantiles (quintiles) for each metric
        # Note: For recency, lower is better, so we invert the scoring
        recency_quantiles = df['recency'].quantile([0.2, 0.4, 0.6, 0.8]).tolist()
        frequency_quantiles = df['frequency'].quantile([0.2, 0.4, 0.6, 0.8]).tolist()
        monetary_quantiles = df['monetary'].quantile([0.2, 0.4, 0.6, 0.8]).tolist()

        # Calculate scores
        scores = []
        for row in rfm_data:
            # Recency: Lower is better, so invert the score (5 - score)
            r_score = 6 - self._calculate_score(row["recency"], recency_quantiles)
            f_score = self._calculate_score(row["frequency"], frequency_quantiles)
            m_score = self._calculate_score(row["monetary"], monetary_quantiles)

            score = RFMScore(
                customer_id=row['customer_id'],
                recency=row['recency'],
                frequency=row['frequency'],
                monetary=Decimal(str(row['monetary'])),
                r_score=r_score,
                f_score=f_score,
                m_score=m_score,
            )

            scores.append(score)
        return scores

    def get_segment_summary(self, scores: List[RFMScore]) -> Dict[str, Dict[str, Any]]:
        """
        Get summary statistics for each customer segment.

        Args:
            scores: List of RFMScore objects

        Returns:
            Dictionary with segment names as keys and stats as values
        """
        df = pd.DataFrame([
            {
                'customer_id': s.customer_id,
                'segment': s.segment,
                'recency': s.recency,
                'frequency': s.frequency,
                'monetary': float(s.monetary),
            }
            for s in scores
        ])

        summary = {}
        for segment in df['segment'].unique():
            segment_df = df[df['segment'] == segment]

            summary[segment] = {
                'count': len(segment_df),
                'avg_recency': round(segment_df['recency'].mean(), 2),
                'avg_frequency': round(segment_df['frequency'].mean(), 2),
                'avg_monetary': round(segment_df['monetary'].mean(), 2),
                'total_monetary': round(segment_df['monetary'].sum(), 2),
            }

        return summary