"""
Fixtures and configuration for pytest.
"""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Fixture for DRF API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(db, django_user_model):
    """Fixture for authenticated API client."""
    user = django_user_model.objects.create_user(
        username='testuser',
        password='testpass123'
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client
