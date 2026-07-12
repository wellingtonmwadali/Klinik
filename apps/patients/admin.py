from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'date_of_birth', 'gender', 'email', 'is_active']
    list_filter = ['gender', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date_of_birth'
