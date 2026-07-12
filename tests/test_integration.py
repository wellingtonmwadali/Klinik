"""
Integration tests for the Klinik API.
"""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestHealthCheck:
    """Test the health check endpoint."""
    
    def test_health_check_returns_200(self, api_client):
        """Test that health check endpoint returns 200 OK."""
        url = reverse('health-check')
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
        assert response.json()['service'] == 'klinik-api'
