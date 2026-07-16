from django.contrib import admin

from .models import Appointment, AppointmentHistory, AppointmentSlot, RescheduleRequest


class AppointmentHistoryInline(admin.TabularInline):
    model = AppointmentHistory
    extra = 0
    readonly_fields = ("action", "changed_by", "changed_at", "previous_values", "new_values")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "appointment_number",
        "patient",
        "doctor",
        "start_datetime",
        "status",
        "reschedule_count",
        "created_at",
    ]
    list_filter = ["status", "start_datetime", "created_at", "doctor"]
    search_fields = [
        "appointment_number",
        "patient__first_name",
        "patient__last_name",
        "doctor__first_name",
        "doctor__last_name",
        "idempotency_key",
    ]
    date_hierarchy = "start_datetime"
    readonly_fields = [
        "appointment_number",
        "idempotency_key",
        "created_at",
        "updated_at",
        "created_by",
        "cancelled_at",
        "cancelled_by",
        "confirmed_at",
    ]
    inlines = [AppointmentHistoryInline]

    fieldsets = (
        (
            "Appointment Details",
            {
                "fields": (
                    "appointment_number",
                    "idempotency_key",
                    "patient",
                    "doctor",
                    "start_datetime",
                    "end_datetime",
                    "duration_minutes",
                )
            },
        ),
        ("Status", {"fields": ("status", "reason_for_visit", "doctor_notes")}),
        (
            "Rescheduling",
            {"fields": ("previous_appointment", "reschedule_count"), "classes": ("collapse",)},
        ),
        (
            "Cancellation",
            {
                "fields": (
                    "cancellation_reason",
                    "cancellation_allowed_until",
                    "cancelled_at",
                    "cancelled_by",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Confirmation & Reminders",
            {"fields": ("confirmed_at", "reminder_sent_at"), "classes": ("collapse",)},
        ),
        (
            "Audit Trail",
            {
                "fields": ("created_at", "created_by", "updated_at", "client_ip", "user_agent"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    list_display = ("appointment", "action", "changed_by", "changed_at")
    list_filter = ("action", "changed_at")
    search_fields = ("appointment__appointment_number", "notes")
    readonly_fields = (
        "appointment",
        "action",
        "previous_values",
        "new_values",
        "changed_by",
        "changed_at",
        "client_ip",
        "user_agent",
    )
    date_hierarchy = "changed_at"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ("doctor", "start_datetime", "end_datetime", "is_available", "appointment")
    list_filter = ("is_available", "doctor", "start_datetime")
    search_fields = ("doctor__first_name", "doctor__last_name")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "start_datetime"


@admin.register(RescheduleRequest)
class RescheduleRequestAdmin(admin.ModelAdmin):
    list_display = (
        "original_appointment",
        "requested_start_datetime",
        "status",
        "requested_by",
        "requested_at",
    )
    list_filter = ("status", "requested_at", "processed_at")
    search_fields = ("original_appointment__appointment_number", "reason")
    readonly_fields = (
        "original_appointment",
        "requested_by",
        "requested_at",
        "processed_by",
        "processed_at",
    )
    date_hierarchy = "requested_at"

    fieldsets = (
        (
            "Request Details",
            {
                "fields": (
                    "original_appointment",
                    "requested_start_datetime",
                    "requested_end_datetime",
                    "reason",
                )
            },
        ),
        ("Status", {"fields": ("status", "rejection_reason", "new_appointment")}),
        (
            "Audit",
            {
                "fields": ("requested_by", "requested_at", "processed_by", "processed_at"),
                "classes": ("collapse",),
            },
        ),
    )
