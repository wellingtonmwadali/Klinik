"""Tests for Doctor app."""

from datetime import date, time, timedelta

import pytest
from rest_framework.test import APIClient

from apps.doctors.models import Doctor, DoctorWorkSchedule
from apps.doctors.services import AvailabilityService


def next_weekday(weekday: int, weeks_ahead: int = 1) -> date:
    today = date.today()
    days_ahead = (weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    days_ahead += 7 * (weeks_ahead - 1)
    return today + timedelta(days=days_ahead)


def make_doctor(**overrides):
    defaults = dict(
        first_name="Jane",
        last_name="Smith",
        email=f"jane.smith.{overrides.get('license_number', 'x')}@clinic.com",
        phone="5551234567",
        specialization="General Practice",
        license_number=overrides.get('license_number', 'MD-TEST-0001'),
        consultation_duration=30,
        max_advance_booking_days=30,
        is_accepting_appointments=True,
        status=Doctor.STATUS_ACTIVE,
        is_active=True,
    )
    defaults.update(overrides)
    return Doctor.objects.create(**defaults)


def make_working_day(doctor, weekday, effective_from, effective_until=None):
    return DoctorWorkSchedule.objects.create(
        doctor=doctor,
        weekday=weekday,
        start_time=time(9, 0),
        end_time=time(18, 0),
        break_start_time=time(12, 0),
        break_end_time=time(13, 0),
        effective_from=effective_from,
        effective_until=effective_until,
    )


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


@pytest.mark.django_db
class TestDoctorAvailabilityService:
    """Tests for schedule-driven doctor availability."""

    def test_availability_uses_active_work_schedule(self):
        doctor = make_doctor(license_number="MD-AVAIL-001")
        target_date = next_weekday(DoctorWorkSchedule.MONDAY)
        make_working_day(doctor, DoctorWorkSchedule.MONDAY, effective_from=date.today())

        availability = AvailabilityService.calculate_available_slots(doctor, target_date)

        assert availability["total_slots"] > 0
        assert availability["work_hours"]["start"] == "09:00:00"
        assert availability["work_hours"]["end"] == "18:00:00"
        assert availability["work_hours"]["break_start"] == "12:00:00"
        assert availability["work_hours"]["break_end"] == "13:00:00"

    def test_availability_returns_no_slots_for_off_day(self):
        doctor = make_doctor(license_number="MD-AVAIL-002")
        make_working_day(doctor, DoctorWorkSchedule.MONDAY, effective_from=date.today())
        target_date = next_weekday(DoctorWorkSchedule.SUNDAY)

        availability = AvailabilityService.calculate_available_slots(doctor, target_date)

        assert availability["total_slots"] == 0
        assert availability["work_hours"] is None
        assert "does not work" in availability["message"].lower()

    def test_availability_ignores_expired_schedule(self):
        doctor = make_doctor(license_number="MD-AVAIL-003")
        expired_from = date.today() - timedelta(days=30)
        expired_until = date.today() - timedelta(days=1)
        make_working_day(
            doctor,
            DoctorWorkSchedule.MONDAY,
            effective_from=expired_from,
            effective_until=expired_until,
        )
        target_date = next_weekday(DoctorWorkSchedule.MONDAY)

        availability = AvailabilityService.calculate_available_slots(doctor, target_date)

        assert availability["total_slots"] == 0
        assert availability["work_hours"] is None


@pytest.mark.django_db
class TestDoctorAvailabilityEndpoint:
    """Integration tests for doctor availability endpoint."""

    def test_availability_endpoint_returns_slots_for_scheduled_day(self):
        doctor = make_doctor(license_number="MD-AVAIL-004")
        target_date = next_weekday(DoctorWorkSchedule.MONDAY)
        make_working_day(doctor, DoctorWorkSchedule.MONDAY, effective_from=date.today())

        client = APIClient()
        response = client.get(
            f"/api/doctors/{doctor.id}/availability/",
            {"date": target_date.isoformat()},
        )

        assert response.status_code == 200, response.content.decode()
        data = response.json()
        assert data["total_slots"] > 0
        assert data["work_hours"] is not None
        assert data["available_slots"]

    def test_availability_endpoint_returns_off_message_when_no_schedule(self):
        doctor = make_doctor(license_number="MD-AVAIL-005")
        target_date = next_weekday(DoctorWorkSchedule.SUNDAY)

        client = APIClient()
        response = client.get(
            f"/api/doctors/{doctor.id}/availability/",
            {"date": target_date.isoformat()},
        )

        assert response.status_code == 200, response.content.decode()
        data = response.json()
        assert data["total_slots"] == 0
        assert data["work_hours"] is None
        assert "does not work" in data["message"].lower()
