"""Tests for Appointment app."""
import pytest
from django.utils import timezone
from apps.appointments.models import Appointment
from apps.doctors.models import Doctor
from apps.patients.models import Patient


@pytest.mark.django_db
class TestAppointmentModel:
    """Tests for Appointment model."""
    
    def test_create_appointment(self):
        """Test creating an appointment."""
        # Create a patient
        patient = Patient.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            gender='M',
            email='john@example.com',
            phone='1234567890',
            address='123 Main St',
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='0987654321'
        )
        
        # Create a doctor
        doctor = Doctor.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@clinic.com',
            phone='5551234567',
            specialization='General Practice',
            license_number='MD12345'
        )
        
        # Create an appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=timezone.now(),
            status='scheduled'
        )
        
        assert appointment.patient == patient
        assert appointment.doctor == doctor
        assert appointment.status == 'scheduled'
        assert str(appointment) is not None
