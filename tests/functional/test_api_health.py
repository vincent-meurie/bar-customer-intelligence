"""
Functional tests for API endpoints
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
@pytest.mark.functional
class TestAPIHealth:
    """Test API health check endpoint."""

    def test_health_check_endpoint(self):
        """Test that health check endpoint returns 200."""
        client = APIClient()
        url = reverse('api:health-check')

        response = client.get(url)

        assert response.status_code == 200
        assert response.data['status'] == 'healthy'
        assert 'message' in response.data