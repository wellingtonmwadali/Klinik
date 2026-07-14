from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """User roles for RBAC"""

    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"
    RECEPTIONIST = "RECEPTIONIST"

    ROLE_CHOICES = [
        (PATIENT, "Patient"),
        (DOCTOR, "Doctor"),
        (ADMIN, "Admin"),
        (RECEPTIONIST, "Receptionist"),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "roles"
        ordering = ["name"]

    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    """Extended user model with timezone and role support"""

    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name="users", null=True, blank=True
    )
    timezone = models.CharField(
        max_length=50,
        default="Africa/Nairobi",
        help_text=_("User timezone for appointment display"),
    )
    is_email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["email", "deleted_at"]),
            models.Index(fields=["role", "is_active"]),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    def soft_delete(self):
        """Soft delete user"""
        from django.utils import timezone

        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
