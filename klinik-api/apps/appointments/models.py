from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Appointment(models.Model):
    """Comprehensive appointment model with idempotency and rescheduling support"""

    STATUS_SCHEDULED = "SCHEDULED"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_NO_SHOW = "NO_SHOW"
    STATUS_RESCHEDULED = "RESCHEDULED"

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_NO_SHOW, "No Show"),
        (STATUS_RESCHEDULED, "Rescheduled"),
    ]

    # Unique identifiers
    appointment_number = models.CharField(
        max_length=20, unique=True, editable=False, help_text=_("Human-readable appointment number")
    )
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text=_("Client-provided key to prevent duplicate bookings"),
    )

    # Relationships
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.PROTECT, related_name="appointments"
    )
    doctor = models.ForeignKey(
        "doctors.Doctor", on_delete=models.PROTECT, related_name="appointments"
    )

    # Scheduling
    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(help_text=_("Actual appointment duration"))

    # Rescheduling support
    previous_appointment = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rescheduled_appointments",
        help_text=_("Reference to original appointment if this is a reschedule"),
    )
    reschedule_count = models.PositiveIntegerField(
        default=0, help_text=_("Number of times this appointment has been rescheduled")
    )

    # Status and notes
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED, db_index=True
    )
    reason_for_visit = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True, help_text=_("Private notes by doctor"))
    cancellation_reason = models.TextField(blank=True)

    # Cancellation policy
    cancellation_allowed_until = models.DateTimeField(
        null=True, blank=True, help_text=_("Latest time patient can cancel without penalty")
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cancelled_appointments",
    )

    # Confirmation
    confirmed_at = models.DateTimeField(null=True, blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)

    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_appointments",
    )
    updated_at = models.DateTimeField(auto_now=True)

    # Request metadata for audit
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = "appointments"
        ordering = ["-start_datetime"]
        constraints = [
            # Prevent double-booking same doctor at same time
            models.UniqueConstraint(
                fields=["doctor", "start_datetime"],
                condition=models.Q(status__in=["SCHEDULED", "CONFIRMED", "IN_PROGRESS"]),
                name="unique_doctor_timeslot",
            ),
            models.CheckConstraint(
                check=models.Q(end_datetime__gt=models.F("start_datetime")), name="end_after_start"
            ),
        ]
        indexes = [
            models.Index(fields=["patient", "start_datetime"]),
            models.Index(fields=["doctor", "start_datetime"]),
            models.Index(fields=["status", "start_datetime"]),
            models.Index(fields=["idempotency_key"]),
        ]

    def __str__(self):
        return f"{self.appointment_number} - {self.patient} with {self.doctor} on {self.start_datetime}"

    def save(self, *args, **kwargs):
        if not self.appointment_number:
            self.appointment_number = self._generate_appointment_number()
        if not self.end_datetime and self.start_datetime and self.duration_minutes:
            from datetime import timedelta

            self.end_datetime = self.start_datetime + timedelta(minutes=self.duration_minutes)
        super().save(*args, **kwargs)

    def _generate_appointment_number(self):
        """Generate unique appointment number like APT20240101-0001"""
        from datetime import datetime

        prefix = f"APT{datetime.now().strftime('%Y%m%d')}"
        last_appointment = (
            Appointment.objects.filter(appointment_number__startswith=prefix)
            .order_by("-appointment_number")
            .first()
        )

        if last_appointment:
            last_num = int(last_appointment.appointment_number.split("-")[1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}-{new_num:04d}"

    def can_cancel(self):
        """Check if appointment can be cancelled"""
        if self.status in [self.STATUS_COMPLETED, self.STATUS_CANCELLED, self.STATUS_NO_SHOW]:
            return False
        if self.cancellation_allowed_until and timezone.now() > self.cancellation_allowed_until:
            return False
        return True

    def clean(self):
        """Validate appointment data"""
        if self.start_datetime and self.start_datetime < timezone.now():
            raise ValidationError(_("Cannot book appointments in the past"))

        if self.start_datetime and self.end_datetime and self.end_datetime <= self.start_datetime:
            raise ValidationError(_("End time must be after start time"))


class AppointmentHistory(models.Model):
    """Audit trail for all appointment changes"""

    ACTION_CREATED = "CREATED"
    ACTION_CONFIRMED = "CONFIRMED"
    ACTION_RESCHEDULED = "RESCHEDULED"
    ACTION_CANCELLED = "CANCELLED"
    ACTION_COMPLETED = "COMPLETED"
    ACTION_NO_SHOW = "NO_SHOW"
    ACTION_UPDATED = "UPDATED"

    ACTION_CHOICES = [
        (ACTION_CREATED, "Created"),
        (ACTION_CONFIRMED, "Confirmed"),
        (ACTION_RESCHEDULED, "Rescheduled"),
        (ACTION_CANCELLED, "Cancelled"),
        (ACTION_COMPLETED, "Completed"),
        (ACTION_NO_SHOW, "No Show"),
        (ACTION_UPDATED, "Updated"),
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="history")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    previous_values = models.JSONField(
        null=True, blank=True, help_text=_("JSON snapshot of previous values")
    )
    new_values = models.JSONField(null=True, blank=True, help_text=_("JSON snapshot of new values"))
    notes = models.TextField(blank=True)

    # Audit metadata
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="appointment_changes",
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = "appointment_history"
        ordering = ["-changed_at"]
        indexes = [
            models.Index(fields=["appointment", "-changed_at"]),
            models.Index(fields=["action", "-changed_at"]),
        ]

    def __str__(self):
        return f"{self.appointment.appointment_number} - {self.get_action_display()} at {self.changed_at}"


class AppointmentSlot(models.Model):
    """Pre-generated time slots for faster availability queries"""

    doctor = models.ForeignKey(
        "doctors.Doctor", on_delete=models.CASCADE, related_name="time_slots"
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_available = models.BooleanField(
        default=True, help_text=_("Whether this slot is available for booking")
    )

    # Link to booked appointment if taken
    appointment = models.OneToOneField(
        Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="reserved_slot"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "appointment_slots"
        ordering = ["start_datetime"]
        constraints = [
            models.UniqueConstraint(fields=["doctor", "start_datetime"], name="unique_doctor_slot"),
        ]
        indexes = [
            models.Index(fields=["doctor", "start_datetime", "is_available"]),
            models.Index(fields=["is_available", "start_datetime"]),
        ]

    def __str__(self):
        status = "Available" if self.is_available else "Booked"
        return f"{self.doctor} - {self.start_datetime} ({status})"


class RescheduleRequest(models.Model):
    """Handle atomic rescheduling of appointments"""

    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    original_appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name="reschedule_requests"
    )

    # New requested time
    requested_start_datetime = models.DateTimeField()
    requested_end_datetime = models.DateTimeField()
    reason = models.TextField(blank=True)

    # New appointment created after approval
    new_appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reschedule_source",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Audit
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reschedule_requests"
    )
    requested_at = models.DateTimeField(auto_now_add=True)

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_reschedules",
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        db_table = "reschedule_requests"
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["original_appointment", "status"]),
            models.Index(fields=["status", "-requested_at"]),
        ]

    def __str__(self):
        return f"Reschedule {self.original_appointment.appointment_number} to {self.requested_start_datetime}"
