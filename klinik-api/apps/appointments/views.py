from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.patients.models import Patient
from core.models import Role

from .models import Appointment
from .serializers import (
    AppointmentBookingSerializer,
    AppointmentCancelSerializer,
    AppointmentRescheduleSerializer,
    AppointmentSerializer,
)
from .services import (
    AppointmentBookingService,
    AppointmentCancellationService,
    AppointmentRescheduleService,
    SlotUnavailableError,
)


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
        if self.action == "cancel":
            return AppointmentCancelSerializer
        if self.action == "reschedule":
            return AppointmentRescheduleSerializer
        return AppointmentSerializer

    def get_queryset(self):
        """
        Scope the appointment list/detail queryset by the requesting user's
        role, so patients only ever see their own appointments and doctors
        only ever see appointments on their own calendar. This is what makes
        list/retrieve (and, by extension, get_object() inside the cancel and
        reschedule actions below) safe: an appointment outside the user's
        scope simply doesn't exist as far as this queryset is concerned, so
        it 404s instead of leaking whether it exists.
        """
        queryset = super().get_queryset()
        user = self.request.user
        role_name = user.role.name if user.role else None

        if role_name == Role.PATIENT:
            try:
                patient = user.patient_profile
            except Patient.DoesNotExist:
                return queryset.none()
            return queryset.filter(patient=patient)

        if role_name == Role.DOCTOR:
            doctor = getattr(user, "doctor_profile", None)
            if doctor is None:
                return queryset.none()
            return queryset.filter(doctor=doctor)

        if role_name in (Role.ADMIN, Role.RECEPTIONIST):
            return queryset

        return queryset.none()

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

        if role_name in (Role.ADMIN, Role.RECEPTIONIST, Role.DOCTOR):
            if validated_patient is None:
                raise PermissionDenied("A 'patient' must be specified when booking on behalf of someone.")
            return validated_patient

        raise PermissionDenied("Your account is not permitted to book appointments.")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        patient = self._resolve_patient(request, data.get("patient"))

        role_name = request.user.role.name if request.user.role else None
        if role_name == Role.DOCTOR:
            own_doctor = getattr(request.user, "doctor_profile", None)
            if own_doctor is None or own_doctor.pk != data["doctor"].pk:
                raise PermissionDenied("You can only book appointments on your own calendar.")

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

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """POST /api/appointments/{id}/cancel/  body: {"reason": "..."}

        get_object() below uses the role-scoped get_queryset(), so a patient
        or doctor attempting to cancel an appointment outside their own scope
        gets a 404, not a 403 - it never confirms the appointment exists.
        """
        appointment = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            appointment = AppointmentCancellationService.cancel_appointment(
                appointment=appointment,
                reason=serializer.validated_data["reason"],
                changed_by=request.user,
                client_ip=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        except ValidationError as e:
            return Response(
                {
                    "error": "Validation error",
                    "detail": str(e.message) if hasattr(e, "message") else str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reschedule(self, request, pk=None):
        """POST /api/appointments/{id}/reschedule/
        body: {"doctor": "<uuid>", "start_datetime": "<iso8601 with offset>"}

        Same 404-not-403 scoping as cancel(), via get_object(). Additionally,
        a doctor-role user may only reschedule an appointment onto their own
        calendar, mirroring the equivalent check in create().
        """
        appointment = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.validated_data["doctor"]

        role_name = request.user.role.name if request.user.role else None
        if role_name == Role.DOCTOR:
            own_doctor = getattr(request.user, "doctor_profile", None)
            if own_doctor is None or own_doctor.pk != doctor.pk:
                raise PermissionDenied(
                    "You can only reschedule appointments onto your own calendar."
                )

        try:
            appointment = AppointmentRescheduleService.reschedule_appointment(
                appointment=appointment,
                doctor=doctor,
                start_datetime=serializer.validated_data["start_datetime"],
                changed_by=request.user,
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

        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_200_OK)
