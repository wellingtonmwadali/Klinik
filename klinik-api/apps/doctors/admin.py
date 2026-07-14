from django.contrib import admin

from .models import Doctor, DoctorUnavailability, DoctorWorkSchedule


class DoctorWorkScheduleInline(admin.TabularInline):
    model = DoctorWorkSchedule
    extra = 1
    fields = (
        "weekday",
        "start_time",
        "end_time",
        "effective_from",
        "effective_until",
        "break_start_time",
        "break_end_time",
    )


class DoctorUnavailabilityInline(admin.TabularInline):
    model = DoctorUnavailability
    extra = 0
    fields = ("start_datetime", "end_datetime", "reason", "affects_existing_appointments")
    readonly_fields = ("created_at", "created_by")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "last_name",
        "first_name",
        "specialization",
        "status",
        "is_accepting_appointments",
        "is_active",
    ]
    list_filter = [
        "specialization",
        "status",
        "is_accepting_appointments",
        "is_active",
        "created_at",
    ]
    search_fields = ["first_name", "last_name", "email", "license_number"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [DoctorWorkScheduleInline, DoctorUnavailabilityInline]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "user",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "specialization",
                    "license_number",
                    "bio",
                )
            },
        ),
        (
            "Booking Configuration",
            {
                "fields": (
                    "consultation_duration",
                    "max_advance_booking_days",
                    "is_accepting_appointments",
                )
            },
        ),
        ("Status", {"fields": ("status", "is_active")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(DoctorWorkSchedule)
class DoctorWorkScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "doctor",
        "weekday",
        "start_time",
        "end_time",
        "effective_from",
        "effective_until",
    )
    list_filter = ("weekday", "effective_from")
    search_fields = ("doctor__first_name", "doctor__last_name")
    ordering = ("doctor", "weekday", "start_time")


@admin.register(DoctorUnavailability)
class DoctorUnavailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "doctor",
        "reason",
        "start_datetime",
        "end_datetime",
        "affects_existing_appointments",
    )
    list_filter = ("reason", "affects_existing_appointments", "start_datetime")
    search_fields = ("doctor__first_name", "doctor__last_name", "notes")
    readonly_fields = ("created_at", "created_by")
    ordering = ("-start_datetime",)
