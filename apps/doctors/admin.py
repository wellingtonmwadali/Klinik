from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'specialization', 'email', 'is_active']
    list_filter = ['specialization', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'license_number']
    readonly_fields = ['created_at', 'updated_at']
