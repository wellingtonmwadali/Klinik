"""Tests for Doctor app."""

import pytest

from apps.doctors.models import Doctor


@pytest.mark.django_db
class TestDoctorModel:
    """Tests for Doctor model."""

    def test_create_doctor(self):
        """Test creating a doctor."""
        doctor = Doctor.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@clinic.com",
            phone="5551234567",
            specialization="Cardiology",
            license_number="MD12345",
        )

        assert doctor.full_name == "Jane Smith"
        assert doctor.is_active is True
        assert str(doctor) == "Dr. Jane Smith (Cardiology)"
