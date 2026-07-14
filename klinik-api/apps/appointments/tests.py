"""Tests for the Appointment app, focused on the POST /appointments booking endpoint."""
from datetime import date, datetime, time, timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.appointments.models import Appointment, AppointmentHistory
from apps.appointments.services import AppointmentBookingService, SlotUnavailableError
from apps.doctors.models import Doctor, DoctorWorkSchedule
from apps.doctors.services import AvailabilityService
from apps.patients.models import Patient
from core.models import Role

User = get_user_model()


def next_weekday(weekday: int, weeks_ahead: int = 1) -> date:
    """Next date (at least `weeks_ahead` weeks out) that falls on the given weekday."""
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
        license_number="MD-TEST-0001",
        consultation_duration=30,
        max_advance_booking_days=30,
        is_accepting_appointments=True,
        status=Doctor.STATUS_ACTIVE,
        is_active=True,
    )
    defaults.update(overrides)
    return Doctor.objects.create(**defaults)


def give_doctor_a_working_day(doctor, weekday, effective_from):
    return DoctorWorkSchedule.objects.create(
        doctor=doctor,
        weekday=weekday,
        start_time=time(9, 0),
        end_time=time(18, 0),
        break_start_time=time(12, 0),
        break_end_time=time(13, 0),
        effective_from=effective_from,
    )


def make_patient(**overrides):
    defaults = dict(
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1990, 1, 1),
        gender="M",
        email="john.doe@example.com",
        phone="1234567890",
        address="123 Main St",
        emergency_contact_name="Jane Doe",
        emergency_contact_phone="0987654321",
        status=Patient.STATUS_ACTIVE,
        is_active=True,
    )
    defaults.update(overrides)
    return Patient.objects.create(**defaults)


def make_user_with_role(role_name, **overrides):
    role, _ = Role.objects.get_or_create(name=role_name, defaults={"description": role_name})
    defaults = dict(username=f"user-{role_name.lower()}-{overrides.get('email', 'x')}", role=role)
    defaults.update({k: v for k, v in overrides.items() if k != "email"})
    return User.objects.create_user(**defaults)


@pytest.mark.django_db
class TestAppointmentModel:
    """Sanity tests for the Appointment model itself."""

    def test_create_appointment(self):
        patient = make_patient()
        doctor = make_doctor()
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            start_datetime=timezone.now() + timedelta(days=1),
            duration_minutes=30,
            idempotency_key="test-key-1",
            status=Appointment.STATUS_SCHEDULED,
        )

        assert appointment.patient == patient
        assert appointment.doctor == doctor
        assert appointment.status == Appointment.STATUS_SCHEDULED
        assert appointment.end_datetime == appointment.start_datetime + timedelta(minutes=30)
        assert str(appointment) is not None


@pytest.mark.django_db
class TestAppointmentBookingService:
    """Tests for AppointmentBookingService.book_appointment directly."""

    def _setup(self):
        doctor = make_doctor()
        patient = make_patient()
        target_date = next_weekday(DoctorWorkSchedule.MONDAY)
        give_doctor_a_working_day(doctor, DoctorWorkSchedule.MONDAY, effective_from=date.today())
        availability = AvailabilityService.calculate_available_slots(doctor, target_date)
        first_slot = availability["available_slots"][0]
        start_dt = datetime.fromisoformat(first_slot["start_datetime"])
        return doctor, patient, start_dt

    def test_valid_booking_creates_appointment_and_history(self):
        doctor, patient, start_dt = self._setup()

        appointment, created = AppointmentBookingService.book_appointment(
            doctor=doctor, patient=patient, start_datetime=start_dt,
        )

        assert created is True
        assert appointment.doctor == doctor
        assert appointment.patient == patient
        assert appointment.start_datetime == start_dt
        assert appointment.duration_minutes == doctor.consultation_duration
        assert AppointmentHistory.objects.filter(
            appointment=appointment, action=AppointmentHistory.ACTION_CREATED
        ).exists()

    def test_doctor_not_accepting_appointments_rejected(self):
        doctor, patient, start_dt = self._setup()
        doctor.is_accepting_appointments = False
        doctor.save()

        with pytest.raises(Exception):
            AppointmentBookingService.book_appointment(
                doctor=doctor, patient=patient, start_datetime=start_dt,
            )

    def test_past_date_rejected(self):
        doctor, patient, _ = self._setup()
        past_dt = timezone.now() - timedelta(days=1)

        with pytest.raises(Exception):
            AppointmentBookingService.book_appointment(
                doctor=doctor, patient=patient, start_datetime=past_dt,
            )

    def test_slot_not_on_grid_rejected_with_409_style_error(self):
        doctor, patient, start_dt = self._setup()
        off_grid_dt = start_dt + timedelta(minutes=1)

        with pytest.raises(SlotUnavailableError) as exc_info:
            AppointmentBookingService.book_appointment(
                doctor=doctor, patient=patient, start_datetime=off_grid_dt,
            )
        assert exc_info.value.available_slots

    def test_already_booked_slot_rejected(self):
        doctor, patient, start_dt = self._setup()
        other_patient = make_patient(email="second.patient@example.com")

        AppointmentBookingService.book_appointment(
            doctor=doctor, patient=patient, start_datetime=start_dt,
        )

        with pytest.raises(SlotUnavailableError):
            AppointmentBookingService.book_appointment(
                doctor=doctor, patient=other_patient, start_datetime=start_dt,
            )

    def test_race_condition_translates_to_slot_unavailable_not_500(self):
        """Simulate: another request books the slot after our availability check
        already ran, so the DB unique constraint is what actually catches it."""
        doctor, patient, start_dt = self._setup()
        other_patient = make_patient(email="racer@example.com")

        # Book the slot for real first (represents the concurrent winner).
        AppointmentBookingService.book_appointment(
            doctor=doctor, patient=other_patient, start_datetime=start_dt,
        )

        # Force our own availability check to (incorrectly) report the slot as free,
        # simulating a check that ran just before the concurrent booking landed.
        stale_availability = AvailabilityService.calculate_available_slots(
            doctor, start_dt.date()
        )
        stale_availability["available_slots"] = [
            {
                "start_time": start_dt.time().isoformat(),
                "end_time": (start_dt + timedelta(minutes=doctor.consultation_duration)).time().isoformat(),
                "start_datetime": start_dt.isoformat(),
                "end_datetime": (start_dt + timedelta(minutes=doctor.consultation_duration)).isoformat(),
            }
        ]
        with patch.object(
            AvailabilityService, "calculate_available_slots", return_value=stale_availability
        ):
            with pytest.raises(SlotUnavailableError):
                AppointmentBookingService.book_appointment(
                    doctor=doctor, patient=patient, start_datetime=start_dt,
                )

        # Only the original (winning) booking exists.
        assert Appointment.objects.filter(doctor=doctor, start_datetime=start_dt).count() == 1

    def test_idempotency_replay_returns_existing_appointment(self):
        doctor, patient, start_dt = self._setup()

        appointment_1, created_1 = AppointmentBookingService.book_appointment(
            doctor=doctor, patient=patient, start_datetime=start_dt, idempotency_key="retry-key",
        )
        appointment_2, created_2 = AppointmentBookingService.book_appointment(
            doctor=doctor, patient=patient, start_datetime=start_dt, idempotency_key="retry-key",
        )

        assert created_1 is True
        assert created_2 is False
        assert appointment_1.pk == appointment_2.pk
        assert Appointment.objects.filter(idempotency_key="retry-key").count() == 1

    def test_inactive_patient_rejected(self):
        doctor, patient, start_dt = self._setup()
        patient.is_active = False
        patient.save()

        with pytest.raises(Exception):
            AppointmentBookingService.book_appointment(
                doctor=doctor, patient=patient, start_datetime=start_dt,
            )


@pytest.mark.django_db
class TestAppointmentBookingEndpoint:
    """Integration tests for POST /api/appointments/."""

    def _setup(self):
        doctor = make_doctor()
        target_date = next_weekday(DoctorWorkSchedule.MONDAY)
        give_doctor_a_working_day(doctor, DoctorWorkSchedule.MONDAY, effective_from=date.today())
        availability = AvailabilityService.calculate_available_slots(doctor, target_date)
        start_datetime = availability["available_slots"][0]["start_datetime"]
        return doctor, start_datetime

    def test_unauthenticated_request_rejected(self):
        doctor, start_datetime = self._setup()
        client = APIClient()

        response = client.post(
            "/api/appointments/",
            {"doctor": doctor.id, "start_datetime": start_datetime},
            format="json",
        )

        # 403, not 401: the project only configures SessionAuthentication, which has no
        # WWW-Authenticate challenge, so DRF's standard behavior for an anonymous
        # request without a challenge-capable authenticator is 403 Forbidden.
        assert response.status_code == 403

    def test_patient_can_book_for_self(self):
        doctor, start_datetime = self._setup()
        patient = make_patient()
        user = make_user_with_role(Role.PATIENT, email=patient.email)
        patient.user = user
        patient.save()

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/appointments/",
            {"doctor": doctor.id, "start_datetime": start_datetime},
            format="json",
        )

        assert response.status_code == 201, response.data
        assert response.data["patient"] == patient.id

    def test_patient_cannot_book_for_another_patient(self):
        doctor, start_datetime = self._setup()
        patient = make_patient()
        other_patient = make_patient(email="other@example.com")
        user = make_user_with_role(Role.PATIENT, email=patient.email)
        patient.user = user
        patient.save()

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/appointments/",
            {"doctor": doctor.id, "patient": other_patient.id, "start_datetime": start_datetime},
            format="json",
        )

        assert response.status_code == 403

    def test_receptionist_can_book_on_behalf_of_patient(self):
        doctor, start_datetime = self._setup()
        patient = make_patient()
        user = make_user_with_role(Role.RECEPTIONIST, email="reception@example.com")

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/appointments/",
            {"doctor": doctor.id, "patient": patient.id, "start_datetime": start_datetime},
            format="json",
        )

        assert response.status_code == 201, response.data
        assert response.data["patient"] == patient.id

    def test_receptionist_cannot_book_for_inactive_patient(self):
        doctor, start_datetime = self._setup()
        patient = make_patient(is_active=False)
        user = make_user_with_role(Role.RECEPTIONIST, email="reception2@example.com")

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/appointments/",
            {"doctor": doctor.id, "patient": patient.id, "start_datetime": start_datetime},
            format="json",
        )

        assert response.status_code == 400

    def test_naive_datetime_rejected(self):
        doctor, start_datetime = self._setup()
        patient = make_patient()
        user = make_user_with_role(Role.RECEPTIONIST, email="reception3@example.com")
        naive = start_datetime.split("+")[0]  # strip timezone offset

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/appointments/",
            {"doctor": doctor.id, "patient": patient.id, "start_datetime": naive},
            format="json",
        )

        assert response.status_code == 400

    def test_double_booking_same_slot_returns_409(self):
        doctor, start_datetime = self._setup()
        patient_a = make_patient(email="a@example.com")
        patient_b = make_patient(email="b@example.com")
        user_a = make_user_with_role(Role.RECEPTIONIST, email="deska@example.com")

        client = APIClient()
        client.force_authenticate(user=user_a)
        first = client.post(
            "/api/appointments/",
            {"doctor": doctor.id, "patient": patient_a.id, "start_datetime": start_datetime},
            format="json",
        )
        assert first.status_code == 201

        second = client.post(
            "/api/appointments/",
            {"doctor": doctor.id, "patient": patient_b.id, "start_datetime": start_datetime},
            format="json",
        )
        assert second.status_code == 409
        assert "available_slots" in second.data
