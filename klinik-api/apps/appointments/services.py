
"""Service layer for appointment booking."""

import uuid
from datetime import datetime, timezone as dt_timezone
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.doctors.models import Doctor
from apps.doctors.services import AvailabilityService
from apps.patients.models import Patient

from .models import Appointment, AppointmentHistory


class SlotUnavailableError(Exception):
    """
    Raised when the requested slot isn't bookable right now
    (already taken, outside working hours, during a break,
    doctor unavailable, etc.).
    """

    def __init__(self, message: str, available_slots: Optional[list] = None):
        super().__init__(message)
        self.message = message
        self.available_slots = available_slots or []


class IdempotencyKeyConflictError(Exception):
    """
    Raised when an idempotency key is reused with request details that
    don't match the appointment originally created under that key
    (different doctor, patient, or start time). This is a client bug
    or a key collision, not a safe replay, so we refuse to silently
    hand back the mismatched appointment.
    """

    def __init__(self, message: str, existing_appointment: "Appointment"):
        super().__init__(message)
        self.message = message
        self.existing_appointment = existing_appointment


class AppointmentBookingService:
    """
    Service responsible for validating and booking appointments.
    """

    @staticmethod
    def _parse_slot_datetime(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def validate_slot(
        *,
        doctor: Doctor,
        start_datetime: datetime,
        exclude_appointment_id: Optional[uuid.UUID] = None,
    ) -> datetime:
        """
        Validate that the requested appointment slot is currently available.

        Args:
            doctor: Doctor the slot is being validated against.
            start_datetime: Requested start time.
            exclude_appointment_id: If given, this appointment's own current
                slot is not treated as a conflict. Pass this when rescheduling
                an appointment so it doesn't collide with itself.

        Returns:
            datetime: The calculated appointment end time.

        Raises:
            ValidationError
            SlotUnavailableError
        """

        AvailabilityService._validate_doctor(doctor)

        requested_date = start_datetime.date()

        AvailabilityService._validate_date(
            doctor,
            requested_date,
        )

        availability = AvailabilityService.calculate_available_slots(
            doctor,
            requested_date,
            exclude_appointment_id=exclude_appointment_id,
        )

        requested_utc = start_datetime.astimezone(dt_timezone.utc)

        matching_slot = next(
            (
                slot
                for slot in availability["available_slots"]
                if AppointmentBookingService._parse_slot_datetime(
                    slot["start_datetime"]
                )
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

        return AppointmentBookingService._parse_slot_datetime(
            matching_slot["end_datetime"]
        )

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
        Validate and create an appointment.

        Returns:
            (appointment, created)

        created=False indicates an idempotent replay.

        Raises:
            ValidationError
            SlotUnavailableError
            IdempotencyKeyConflictError: if idempotency_key was already used
                for a different doctor/patient/start_datetime than requested.
        """

        # Handle idempotent retries
        if idempotency_key:
            existing = Appointment.objects.filter(
                idempotency_key=idempotency_key
            ).first()

            if existing is not None:
                # Only treat this as a safe replay if the request matches what
                # was originally booked under this key. Otherwise this is a
                # client bug or a key collision, and silently returning the
                # existing appointment would hand back the wrong booking.
                matches = (
                    existing.doctor_id == doctor.id
                    and existing.patient_id == patient.id
                    and existing.start_datetime == start_datetime
                )
                if not matches:
                    raise IdempotencyKeyConflictError(
                        "This idempotency key was already used for a different "
                        "appointment request (different doctor, patient, or "
                        "start time). Please use a new idempotency key.",
                        existing_appointment=existing,
                    )
                return existing, False

        # Validate patient
        if (
            not patient.is_active
            or patient.status != Patient.STATUS_ACTIVE
        ):
            raise ValidationError(
                f"Patient {patient.full_name} is not active and cannot book appointments."
            )

        # Validate requested slot
        end_datetime = AppointmentBookingService.validate_slot(
            doctor=doctor,
            start_datetime=start_datetime,
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

        except IntegrityError as exc:
            raise SlotUnavailableError(
                "This slot was just booked by someone else. Please choose another time."
            ) from exc

        AppointmentHistory.objects.create(
            appointment=appointment,
            action=AppointmentHistory.ACTION_CREATED,
            new_values={
                "doctor_id": str(doctor.id),
                "patient_id": str(patient.id),
                "start_datetime": start_datetime.isoformat(),
                "end_datetime": end_datetime.isoformat(),
                "status": appointment.status,
            },
            changed_by=created_by,
            client_ip=client_ip,
            user_agent=user_agent,
        )

        return appointment, True


class AppointmentRescheduleService:
    """Service layer for rescheduling appointments."""

    @staticmethod
    @transaction.atomic
    def reschedule_appointment(
        *,
        appointment: Appointment,
        doctor: Doctor,
        start_datetime: datetime,
        changed_by=None,
        client_ip: Optional[str] = None,
        user_agent: str = "",
    ) -> Appointment:
        """
        Reschedule an existing appointment.

        Raises:
            ValidationError
            SlotUnavailableError
        """

        # Cannot reschedule cancelled appointments
        if appointment.status == Appointment.STATUS_CANCELLED:
            raise ValidationError(
                "Cancelled appointments cannot be rescheduled."
            )

        # Preserve previous values for audit history
        old_values = {
            "doctor_id": str(appointment.doctor.id),
            "patient_id": str(appointment.patient.id),
            "start_datetime": appointment.start_datetime.isoformat(),
            "end_datetime": appointment.end_datetime.isoformat(),
            "status": appointment.status,
        }

        # Validate the new slot using the booking service. Exclude this
        # appointment's own id so its current slot isn't treated as a
        # conflict with the new time being requested.
        end_datetime = AppointmentBookingService.validate_slot(
            doctor=doctor,
            start_datetime=start_datetime,
            exclude_appointment_id=appointment.id,
        )

        # Update appointment
        appointment.doctor = doctor
        appointment.start_datetime = start_datetime
        appointment.end_datetime = end_datetime
        appointment.duration_minutes = doctor.consultation_duration

        try:
            appointment.save()

        except IntegrityError as exc:
            raise SlotUnavailableError(
                "This slot was just booked by another patient. Please choose another time."
            ) from exc

        # Record audit history
        AppointmentHistory.objects.create(
            appointment=appointment,
            action=AppointmentHistory.ACTION_RESCHEDULED,
            previous_values=old_values,
            new_values={
                "doctor_id": str(doctor.id),
                "patient_id": str(appointment.patient.id),
                "start_datetime": start_datetime.isoformat(),
                "end_datetime": end_datetime.isoformat(),
                "status": appointment.status,
            },
            changed_by=changed_by,
            client_ip=client_ip,
            user_agent=user_agent,
        )

        return appointment


class AppointmentCancellationService:
    """Service layer for cancelling appointments."""

    @staticmethod
    @transaction.atomic
    def cancel_appointment(
        *,
        appointment: Appointment,
        reason: str,
        changed_by=None,
        client_ip: Optional[str] = None,
        user_agent: str = "",
    ) -> Appointment:
        """
        Cancel an appointment.

        Raises:
            ValidationError
        """

        # Cannot cancel an appointment twice
        if appointment.status == Appointment.STATUS_CANCELLED:
            raise ValidationError(
                "This appointment has already been cancelled."
            )

        old_values = {
            "status": appointment.status,
            "doctor_id": str(appointment.doctor.id),
            "patient_id": str(appointment.patient.id),
            "start_datetime": appointment.start_datetime.isoformat(),
            "end_datetime": appointment.end_datetime.isoformat(),
        }

        # Cancel appointment
        appointment.status = Appointment.STATUS_CANCELLED
        appointment.cancellation_reason = reason
        appointment.save(
            update_fields=[
                "status",
                "cancellation_reason",
                "updated_at",
            ]
        )

        # Record audit history
        AppointmentHistory.objects.create(
            appointment=appointment,
            action=AppointmentHistory.ACTION_CANCELLED,
             previous_values=old_values,
            new_values={
                "status": Appointment.STATUS_CANCELLED,
                "reason": reason,
            },
            changed_by=changed_by,
            client_ip=client_ip,
            user_agent=user_agent,
        )

        return appointment