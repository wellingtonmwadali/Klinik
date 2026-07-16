from django.utils import timezone as django_timezone
from rest_framework import serializers

from apps.doctors.models import Doctor
from apps.patients.models import Patient

from .models import Appointment


class TimezoneAwareDateTimeField(serializers.DateTimeField):
    """A DateTimeField that rejects naive input instead of silently assuming a timezone.

    DRF's default DateTimeField auto-localizes naive input to the current timezone when
    USE_TZ=True, which would silently guess what the client meant. Booking times are
    ambiguous enough (see the timezone edge cases) without adding a hidden guess on top.
    """

    def enforce_timezone(self, value):
        if django_timezone.is_naive(value):
            raise serializers.ValidationError(
                "This field must include a timezone offset (e.g. 'Z' or '+03:00')."
            )
        return super().enforce_timezone(value)


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for representing an Appointment (read / general CRUD)."""

    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.full_name", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "appointment_number",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "start_datetime",
            "end_datetime",
            "duration_minutes",
            "status",
            "reason_for_visit",
            "reschedule_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "appointment_number",
            "end_datetime",
            "duration_minutes",
            "status",
            "reschedule_count",
            "created_at",
            "updated_at",
        ]


class AppointmentBookingSerializer(serializers.Serializer):
    """Serializer for the POST /appointments booking request body.

    end_datetime/duration_minutes are deliberately absent: they're always
    derived server-side from the matched slot, never trusted from the client.
    """

    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), required=False)
    start_datetime = TimezoneAwareDateTimeField()
    reason_for_visit = serializers.CharField(required=False, allow_blank=True, default="")
    idempotency_key = serializers.CharField(required=False, allow_blank=False, max_length=255)


class AppointmentCancelSerializer(serializers.Serializer):
    """Serializer for the POST /appointments/{id}/cancel/ request body."""

    reason = serializers.CharField(allow_blank=False, max_length=500)


class AppointmentRescheduleSerializer(serializers.Serializer):
    """Serializer for the POST /appointments/{id}/reschedule/ request body.

    Same rationale as AppointmentBookingSerializer: end_datetime is always
    derived server-side from the matched slot, never trusted from the client.
    """

    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    start_datetime = TimezoneAwareDateTimeField()