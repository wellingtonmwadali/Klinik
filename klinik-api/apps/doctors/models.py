import uuid
from datetime import date, datetime, time, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Doctor(models.Model):
    """Doctor profile with work schedule and booking configuration"""

    STATUS_ACTIVE = "ACTIVE"
    STATUS_ON_LEAVE = "ON_LEAVE"
    STATUS_INACTIVE = "INACTIVE"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_ON_LEAVE, "On Leave"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        null=True,
        blank=True,
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True)

    # Booking configuration
    consultation_duration = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(15)],
        help_text=_("Consultation duration in minutes"),
    )
    max_advance_booking_days = models.PositiveIntegerField(
        default=30, help_text=_("Maximum days in advance patients can book")
    )
    is_accepting_appointments = models.BooleanField(
        default=True, help_text=_("Whether the doctor is currently accepting new appointments")
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctors"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["specialization"]),
            models.Index(fields=["status", "is_accepting_appointments"]),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"Dr. {self.full_name} ({self.specialization})"


class DoctorWorkSchedule(models.Model):
    """Doctor's weekly work schedule with support for schedule changes"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    WEEKDAY_CHOICES = [
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday"),
    ]

    # Clinic-wide scheduling rules: a doctor picks any shift within the clinic's
    # operating window, but the shift must span exactly SHIFT_SPAN_HOURS (including
    # a BREAK_HOURS break), and a full week is WORKING_DAYS_PER_WEEK such shifts.
    CLINIC_OPENING_TIME = time(6, 0)
    CLINIC_CLOSING_TIME = time(22, 0)
    SHIFT_SPAN_HOURS = 9
    BREAK_HOURS = 1
    NET_DAILY_HOURS = SHIFT_SPAN_HOURS - BREAK_HOURS
    WORKING_DAYS_PER_WEEK = 5
    WEEKLY_HOURS = NET_DAILY_HOURS * WORKING_DAYS_PER_WEEK

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="work_schedule")
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Support for schedule changes
    effective_from = models.DateField(help_text=_("Date when this schedule becomes effective"))
    effective_until = models.DateField(
        null=True, blank=True, help_text=_("Date when this schedule ends (null = indefinite)")
    )

    # Break time (required: every working day includes exactly one break)
    break_start_time = models.TimeField()
    break_end_time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctor_work_schedule"
        ordering = ["weekday", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "weekday", "start_time", "effective_from"],
                name="unique_doctor_schedule",
            ),
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F("start_time")),
                name="end_time_after_start_time",
            ),
            models.CheckConstraint(
                check=models.Q(start_time__gte=time(6, 0)),
                name="start_time_within_clinic_hours",
            ),
            models.CheckConstraint(
                check=models.Q(end_time__lte=time(22, 0)),
                name="end_time_within_clinic_hours",
            ),
        ]
        indexes = [
            models.Index(fields=["doctor", "effective_from", "effective_until"]),
        ]

    @staticmethod
    def _hours_between(start: time, end: time) -> float:
        """Hours between two times on the same day, as a float."""
        return (datetime.combine(date.min, end) - datetime.combine(date.min, start)) / timedelta(
            hours=1
        )

    def clean(self):
        errors = {}

        if self.start_time and self.start_time < self.CLINIC_OPENING_TIME:
            errors["start_time"] = _(
                f"Start time cannot be before clinic opening time ({self.CLINIC_OPENING_TIME})."
            )
        if self.end_time and self.end_time > self.CLINIC_CLOSING_TIME:
            errors["end_time"] = _(
                f"End time cannot be after clinic closing time ({self.CLINIC_CLOSING_TIME})."
            )

        if self.start_time and self.end_time and self.end_time > self.start_time:
            span = self._hours_between(self.start_time, self.end_time)
            if span != self.SHIFT_SPAN_HOURS:
                errors["end_time"] = _(
                    f"A working day must span exactly {self.SHIFT_SPAN_HOURS} hours "
                    f"(start to end); got {span} hours."
                )

        if self.break_start_time and self.break_end_time:
            if self.break_end_time > self.break_start_time:
                break_span = self._hours_between(self.break_start_time, self.break_end_time)
                if break_span != self.BREAK_HOURS:
                    errors["break_end_time"] = _(
                        f"Break must be exactly {self.BREAK_HOURS} hour; got {break_span} hours."
                    )
            else:
                errors["break_end_time"] = _("Break end time must be after break start time.")

            if self.start_time and self.break_start_time < self.start_time:
                errors["break_start_time"] = _("Break must start after the shift start time.")
            if self.end_time and self.break_end_time > self.end_time:
                errors["break_end_time"] = _("Break must end before the shift end time.")

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.doctor.full_name} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class DoctorUnavailability(models.Model):
    """Track doctor unavailability (vacation, sick leave, emergency)"""

    REASON_VACATION = "VACATION"
    REASON_SICK_LEAVE = "SICK_LEAVE"
    REASON_EMERGENCY = "EMERGENCY"
    REASON_CONFERENCE = "CONFERENCE"
    REASON_OTHER = "OTHER"

    REASON_CHOICES = [
        (REASON_VACATION, "Vacation"),
        (REASON_SICK_LEAVE, "Sick Leave"),
        (REASON_EMERGENCY, "Emergency"),
        (REASON_CONFERENCE, "Conference"),
        (REASON_OTHER, "Other"),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="unavailability")
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    notes = models.TextField(blank=True)

    affects_existing_appointments = models.BooleanField(
        default=False,
        help_text=_(
            "If True, existing appointments in this period will be flagged for rescheduling"
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_unavailability",
    )

    class Meta:
        db_table = "doctor_unavailability"
        ordering = ["-start_datetime"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_datetime__gt=models.F("start_datetime")),
                name="unavailability_end_after_start",
            ),
        ]
        indexes = [
            models.Index(fields=["doctor", "start_datetime", "end_datetime"]),
        ]

    def __str__(self):
        return (
            f"{self.doctor.full_name} - {self.get_reason_display()} ({self.start_datetime.date()})"
        )
