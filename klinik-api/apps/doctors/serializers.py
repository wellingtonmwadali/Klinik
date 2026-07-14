from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Doctor, DoctorWorkSchedule


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model."""

    full_name = serializers.CharField(read_only=True)
    appointment_count = serializers.IntegerField(source="appointments.count", read_only=True)

    class Meta:
        model = Doctor
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "specialization",
            "license_number",
            "is_active",
            "bio",
            "appointment_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class DoctorWorkScheduleSerializer(serializers.ModelSerializer):
    """Serializer for a single day of a doctor's weekly work schedule."""

    class Meta:
        model = DoctorWorkSchedule
        fields = [
            "weekday",
            "start_time",
            "end_time",
            "break_start_time",
            "break_end_time",
            "effective_from",
            "effective_until",
        ]


class WorkScheduleDayInputSerializer(serializers.ModelSerializer):
    """Serializer for a single day within a weekly schedule write payload."""

    class Meta:
        model = DoctorWorkSchedule
        fields = [
            "weekday",
            "start_time",
            "end_time",
            "break_start_time",
            "break_end_time",
        ]


class WeeklyScheduleWriteSerializer(serializers.Serializer):
    """Serializer for setting a doctor's full weekly work schedule at once."""

    effective_from = serializers.DateField()
    effective_until = serializers.DateField(required=False, allow_null=True, default=None)
    days = WorkScheduleDayInputSerializer(many=True)

    def validate_effective_from(self, value):
        today = timezone.now().date()
        if value < today:
            raise serializers.ValidationError("Effective from cannot be in the past.")
        return value

    def validate(self, data):
        effective_from = data.get("effective_from")
        effective_until = data.get("effective_until")

        if effective_until is not None and effective_until < effective_from:
            raise serializers.ValidationError(
                {"effective_until": "Effective until must be on or after effective from."}
            )

        if effective_until is not None:
            minimum_until = effective_from + timedelta(weeks=3)
            if effective_until < minimum_until:
                raise serializers.ValidationError(
                    {
                        "effective_until": (
                            "Effective until must be at least 3 weeks after the effective from date."
                        )
                    }
                )

        return data

    def validate_days(self, value):
        if len(value) != DoctorWorkSchedule.WORKING_DAYS_PER_WEEK:
            raise serializers.ValidationError(
                f"Exactly {DoctorWorkSchedule.WORKING_DAYS_PER_WEEK} working days are required; "
                f"got {len(value)}."
            )
        return value


class TimeSlotSerializer(serializers.Serializer):
    """Serializer for individual time slots."""
    
    start_time = serializers.TimeField(help_text="Start time (local time)")
    end_time = serializers.TimeField(help_text="End time (local time)")
    start_datetime = serializers.DateTimeField(help_text="Start datetime in UTC (ISO 8601)")
    end_datetime = serializers.DateTimeField(help_text="End datetime in UTC (ISO 8601)")


class WorkHoursSerializer(serializers.Serializer):
    """Serializer for work hours information."""
    
    start = serializers.TimeField(help_text="Work start time")
    end = serializers.TimeField(help_text="Work end time")
    break_start = serializers.TimeField(allow_null=True, help_text="Break start time")
    break_end = serializers.TimeField(allow_null=True, help_text="Break end time")


class AvailabilityResponseSerializer(serializers.Serializer):
    """Serializer for doctor availability response."""
    
    doctor_id = serializers.IntegerField(help_text="Doctor's ID")
    doctor_name = serializers.CharField(help_text="Doctor's full name with title")
    specialization = serializers.CharField(help_text="Doctor's specialization")
    date = serializers.DateField(help_text="Date for which availability is shown")
    consultation_duration = serializers.IntegerField(help_text="Consultation duration in minutes")
    available_slots = TimeSlotSerializer(many=True, help_text="List of available time slots")
    total_slots = serializers.IntegerField(help_text="Total number of available slots")
    work_hours = WorkHoursSerializer(allow_null=True, help_text="Doctor's work hours for this day")
    message = serializers.CharField(required=False, allow_null=True, help_text="Optional message (e.g., doctor doesn't work this day)")
