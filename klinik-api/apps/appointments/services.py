"""Service layer for appointment booking."""
import uuid
from datetime import datetime, timezone as dt_timezone
from typing import Any, Dict, Optional

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.doctors.models import Doctor
from apps.doctors.services import AvailabilityService
from apps.patients.models import Patient

from .models import Appointment, AppointmentHistory


class SlotUnavailableError(Exception):
    """Raised when the requested slot isn't bookable right now (already taken, outside
    working hours, mid-break, doctor unavailable, etc). Callers should surface this as
    409 Conflict rather than a generic 400 — the request was well-formed, but the world
    changed under it (or was never in the state the client assumed).

    Deliberately not a ValidationError subclass: it carries a structured
    `available_slots` payload, which doesn't fit Django's message/message_dict
    machinery (built for string messages, not arbitrary JSON-able data).
    """

    def __init__(self, message: str, available_slots: Optional[list] = None):
        super().__init__(message)
        self.message = message
        self.available_slots = available_slots or []


class AppointmentBookingService:
    """Books appointments against the same availability grid the availability
    endpoint exposes, so there is exactly one definition of "available"."""

    @staticmethod
    def _parse_slot_datetime(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    @transaction.atomic
    def book_appointment(
        *,
        doctor: Doctor,
        patient: Patient,
        start_datetime: datetime,
        reason_for_visit: str = "",
        created_by=None,
        idempotency_key: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: str = "",
    ) -> tuple[Appointment, bool]:
        """
        Validate and create an Appointment. Raises ValidationError (400-class) for
        ordinary validation failures, or SlotUnavailableError (409-class) when the
        slot itself isn't currently bookable.

        Returns (appointment, created) — created is False for an idempotent replay.
        """
        # Idempotent replay: a client retrying the same request (e.g. after a timeout)
        # gets back the appointment it already created, not a duplicate or an error.
        if idempotency_key:
            existing = Appointment.objects.filter(idempotency_key=idempotency_key).first()
            if existing is not None:
                return existing, False

        if not patient.is_active or patient.status != Patient.STATUS_ACTIVE:
            raise ValidationError(
                f"Patient {patient.full_name} is not active and cannot book appointments."
            )

        AvailabilityService._validate_doctor(doctor)
        requested_date = start_datetime.date()
        AvailabilityService._validate_date(doctor, requested_date)

        availability = AvailabilityService.calculate_available_slots(doctor, requested_date)
        requested_utc = start_datetime.astimezone(dt_timezone.utc)

        matching_slot = next(
            (
                slot
                for slot in availability["available_slots"]
                if AppointmentBookingService._parse_slot_datetime(slot["start_datetime"])
                == requested_utc
            ),
            None,
        )
        if matching_slot is None:
            raise SlotUnavailableError(
                "The requested time is not an available slot for this doctor "
                "(outside working hours, during a break, already booked, or "
                "the doctor is unavailable that day).",
                available_slots=availability["available_slots"],
            )

        end_datetime = AppointmentBookingService._parse_slot_datetime(
            matching_slot["end_datetime"]
        )

        try:
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                duration_minutes=doctor.consultation_duration,
                reason_for_visit=reason_for_visit,
                idempotency_key=idempotency_key or uuid.uuid4().hex,
                created_by=created_by,
                client_ip=client_ip,
                user_agent=user_agent,
            )
        except IntegrityError as e:
            # Simplification: any IntegrityError here is treated as a lost race for the
            # slot (by far the most common cause, given the partial unique constraint on
            # doctor+start_datetime) rather than distinguishing every possible constraint.
            raise SlotUnavailableError(
                "This slot was just booked by someone else. Please choose another time."
            ) from e

        AppointmentHistory.objects.create(
            appointment=appointment,
            action=AppointmentHistory.ACTION_CREATED,
            new_values={
                "doctor_id": doctor.id,
                "patient_id": patient.id,
                "start_datetime": start_datetime.isoformat(),
                "end_datetime": end_datetime.isoformat(),
                "status": appointment.status,
            },
            changed_by=created_by,
            client_ip=client_ip,
            user_agent=user_agent,
        )

        return appointment, True
