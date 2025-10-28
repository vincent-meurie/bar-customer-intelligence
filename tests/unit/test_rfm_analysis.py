"""Unit tests for RFM analysis."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from src.analytics.rfm import RFMAnalyzer, RFMScore

class TestRFMScore:
    """Test RFM Score dataclass"""

    def test_rfm_score_creation(self):
        """Test creating an RFM score."""
        score = RFMScore(
            customer_id="CUST001",
            recency=5,
            frequency=120,
            monetary=Decimal("1500.00"),
            r_score=5,
            f_score=4,
            m_score=5,
        )

        assert score.customer_id == "CUST001"
        assert score.recency == 5
        assert score.frequency == 120
        assert score.monetary == Decimal("1500.00")
        assert score.rfm_score == "545"

    def test_rfm_segment_championship(self):
        """Test champion segment identification."""
        score = RFMScore(
            customer_id="CUST001",
            recency=2,
            frequency=100,
            monetary=Decimal("2000.00"),
            r_score=5,
            f_score=5,
            m_score=5,
        )

        assert score.segment ==  "Champions"

    def test_rfm_segment_loyal(self):
        """Test loyal customer segment."""
        score = RFMScore(
            customer_id="CUST002",
            recency=10,
            frequency=80,
            monetary=Decimal("1200.00"),
            r_score=4,
            f_score=5,
            m_score=4,
        )

        assert score.segment == "Loyal Customers"

    def test_rfm_segment_at_risk(self):
        """Test at-risk segment identification."""
        score = RFMScore(
            customer_id="CUST003",
            rceency=90,
            frequency=50,
            monetary=Decimal("800.00"),
            r_score=2,
            f_score=4,
            m_score=3,
        )

        assert score.segment == "At Risk"

class TestRFMAnalyzer:
    """Test RFM Analyzer."""

    def test_analyzer_initialization(self):
        """Test RFM Analyzer can be initialized."""
        analyzer = RFMAnalyzer()
        assert analyzer is not None

    def test_calculate_recency(self):
        """Test recency calculation (days since last purchase)."""
        analyzer = RFMAnalyzer()

        transactions = [
            {
                "customer_id": "CUST001",
                "transaction_date": datetime.now() - timedelta(days=5),
                "total_amount": Decimal("50.00"),
            },
            {
                "customer_id": "CUST001",
                "transaction_date": datetime.now() - timedelta(days=30),
                "total_amount": Decimal("75.00"),
            },
        ]

        recency = analyzer.calculate_recency("CUST001", transactions)
        assert recency == 5

    def test_calculate_frequency(self):
        """Test frequency calculation (number of purchases)."""
        analyzer = RFMAnalyzer()

        transactions = [
            {"customer_id": "CUST001", "transaction_date": datetime.now(), "total_amount": Decimal("50.00")},
            {"customer_id": "CUST001", "transaction_date": datetime.now() - timedelta(days=10), "total_amount": Decimal("75.00")},
            {"customer_id": "CUST001", "transaction_date": datetime.now() - timedelta(days=20), "total_amount": Decimal("100.00")},
        ]

        frequency = analyzer.calculate_frequency("CUST001", transactions)
        assert frequency == 3

    def test_calculate_monetary(self):
        """Test monetary calculation (total spent)."""
        analyzer = RFMAnalyzer()

        transactions = [
            {"customer_id": "CUST001", "transaction_date": datetime.now(), "total_amount": Decimal("50.00")},
            {"customer_id": "CUST001", "transaction_date": datetime.now() - timedelta(days=10), "total_amount": Decimal("75.00")},
            {"customer_id": "CUST001", "transaction_date": datetime.now() - timedelta(days=20), "total_amount": Decimal("100.00")},
        ]

        monetary = analyzer.calculate_monetary("CUST001", transactions)
        assert monetary == Decimal("225.00")

    def test_calculate_rfm_score(self):
        """Test complete RFM score calculation for multiple customers."""
        analyzer = RFMAnalyzer()

        transactions = [
            # Customer 1: Recent, frequent, high value (Champion)
            {"customer_id": "CUST001", "transaction_date": datetime.now() - timedelta(days=2), "total_amount": Decimal("100.00")},
            {"customer_id": "CUST001", "transaction_date": datetime.now() - timedelta(days=10), "total_amount": Decimal("150.00")},
            {"customer_id": "CUST001", "transaction_date": datetime.now() - timedelta(days=20), "total_amount": Decimal("200.00")},

            # Customer2: Old, infrequent, low value (Lost)
            {"customer_id": "CUST002", "transaction_date": datetime.now() - timedelta(days=180), "total_amount": Decimal("20.00")},
        ]

        scores = analyzer.calculate_rfm_scores(transactions)

        assert len(scores) == 2
        assert scores[0].customer_id in ["CUST001", "CUST002"]
        assert all(hasattr(score, 'r_score') for score in scores)
        assert all(hasattr(score, 'f_score') for score in scores)
        assert all(hasattr(score, 'm_score') for score in scores)

