from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.patients.models import Patient
from core.models import Role

from .models import Appointment
from .serializers import AppointmentBookingSerializer, AppointmentSerializer
from .services import AppointmentBookingService, SlotUnavailableError


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing appointments."""

    queryset = Appointment.objects.select_related("patient", "doctor").all()
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "doctor", "patient"]
    search_fields = [
        "patient__first_name",
        "patient__last_name",
        "doctor__first_name",
        "doctor__last_name",
    ]
    ordering_fields = ["start_datetime", "created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return AppointmentBookingSerializer
        return AppointmentSerializer

    def _resolve_patient(self, request, validated_patient):
        """Determine who the appointment is being booked for, based on the
        requesting user's role. Patients may only book for themselves; staff
        (admin/receptionist) may book on behalf of any patient they specify."""
        role_name = request.user.role.name if request.user.role else None

        if role_name == Role.PATIENT:
            try:
                own_patient = request.user.patient_profile
            except Patient.DoesNotExist:
                raise PermissionDenied(
                    "Your account has no linked patient profile, so it cannot book "
                    "appointments."
                )
            if validated_patient is not None and validated_patient.pk != own_patient.pk:
                raise PermissionDenied("You cannot book an appointment on behalf of another patient.")
            return own_patient

        if role_name in (Role.ADMIN, Role.RECEPTIONIST):
            if validated_patient is None:
                raise PermissionDenied("A 'patient' must be specified when booking on behalf of someone.")
            return validated_patient

        raise PermissionDenied("Your account is not permitted to book appointments.")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        patient = self._resolve_patient(request, data.get("patient"))

        try:
            appointment, created = AppointmentBookingService.book_appointment(
                doctor=data["doctor"],
                patient=patient,
                start_datetime=data["start_datetime"],
                reason_for_visit=data.get("reason_for_visit", ""),
                created_by=request.user,
                idempotency_key=data.get("idempotency_key"),
                client_ip=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        except SlotUnavailableError as e:
            return Response(
                {
                    "error": "Slot unavailable",
                    "detail": e.message,
                    "available_slots": e.available_slots,
                },
                status=status.HTTP_409_CONFLICT,
            )
        except ValidationError as e:
            return Response(
                {
                    "error": "Validation error",
                    "detail": str(e.message) if hasattr(e, "message") else str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = AppointmentSerializer(appointment)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED,
        )
