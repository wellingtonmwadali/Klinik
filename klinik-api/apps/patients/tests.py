"""Tests for Patient app."""

import pytest

from apps.patients.models import Patient


@pytest.mark.django_db
class TestPatientModel:
    """Tests for Patient model."""

    def test_create_patient(self):
        """Test creating a patient."""
        patient = Patient.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            gender="M",
            email="john@example.com",
            phone="1234567890",
            address="123 Main St",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="0987654321",
        )

        assert patient.full_name == "John Doe"
        assert patient.is_active is True
        assert str(patient) == "John Doe"
