from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "last_name",
        "first_name",
        "date_of_birth",
        "gender",
        "blood_group",
        "status",
        "is_active",
    ]
    list_filter = ["gender", "blood_group", "status", "is_active", "created_at"]
    search_fields = ["first_name", "last_name", "email", "phone", "insurance_policy_number"]
    readonly_fields = ["created_at", "updated_at", "age"]
    date_hierarchy = "date_of_birth"

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "user",
                    "first_name",
                    "last_name",
                    "date_of_birth",
                    "age",
                    "gender",
                    "email",
                    "phone",
                    "address",
                )
            },
        ),
        (
            "Medical Information",
            {
                "fields": (
                    "blood_group",
                    "medical_history",
                    "allergies",
                    "current_medications",
                    "medical_notes",
                )
            },
        ),
        (
            "Emergency Contact",
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_contact_phone",
                    "emergency_contact_relationship",
                )
            },
        ),
        (
            "Insurance",
            {
                "fields": (
                    "insurance_provider",
                    "insurance_policy_number",
                    "insurance_expiry_date",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Status", {"fields": ("status", "is_active")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
