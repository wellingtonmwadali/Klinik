from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Doctor, DoctorWorkSchedule
from .serializers import (
    DoctorSerializer,
    AvailabilityResponseSerializer,
    DoctorWorkScheduleSerializer,
    WeeklyScheduleWriteSerializer,
)
from .services import AvailabilityService, WorkScheduleService


class DoctorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing doctors."""

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["specialization", "is_active"]
    search_fields = ["first_name", "last_name", "specialization", "email"]
    ordering_fields = ["last_name", "created_at"]

    def get_permissions(self):
        """
        Set permissions based on action:
        - list, retrieve, availability: Public (AllowAny)
        - work_schedule: Public (GET) / Admin only (PUT)
        - create, update, partial_update, destroy: Admin only
        """
        if self.action in ['list', 'retrieve', 'availability']:
            permission_classes = [AllowAny]
        elif self.action == 'work_schedule' and self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get', 'put'], url_path='work-schedule')
    def work_schedule(self, request, pk=None):
        """
        Get or set a doctor's current weekly work schedule.

        GET: returns the doctor's currently effective schedule (one entry per working day).
        PUT: replaces the doctor's schedule for a given effective period. Body:
            {
                "effective_from": "2026-07-20",
                "effective_until": null,
                "days": [
                    {"weekday": 0, "start_time": "09:00", "end_time": "18:00",
                     "break_start_time": "12:00", "break_end_time": "13:00"},
                    ... exactly 5 entries, distinct weekdays ...
                ]
            }
        """
        doctor = get_object_or_404(Doctor, pk=pk)

        if request.method == 'GET':
            today = timezone.now().date()
            schedules = DoctorWorkSchedule.objects.filter(
                doctor=doctor,
                effective_from__lte=today,
            ).filter(
                models.Q(effective_until__isnull=True) | models.Q(effective_until__gte=today)
            )
            serializer = DoctorWorkScheduleSerializer(schedules, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # PUT
        serializer = WeeklyScheduleWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            instances = WorkScheduleService.set_weekly_schedule(
                doctor=doctor,
                days=serializer.validated_data['days'],
                effective_from=serializer.validated_data['effective_from'],
                effective_until=serializer.validated_data.get('effective_until'),
            )
        except ValidationError as e:
            return Response(
                {
                    'error': 'Validation error',
                    'detail': e.message_dict if hasattr(e, 'message_dict') else str(e),
                    'doctor': f"Dr. {doctor.full_name}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            DoctorWorkScheduleSerializer(instances, many=True).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['get'], url_path='availability')
    def availability(self, request, pk=None):
        """
        Get available time slots for a doctor on a specific date.
        
        Query Parameters:
            date (required): Date in YYYY-MM-DD format
            
        Returns:
            200: Available slots with metadata
            400: Validation error (invalid date, doctor unavailable, etc.)
            404: Doctor not found
            
        Example:
            GET /api/doctors/1/availability/?date=2026-07-15
        """
        # Get doctor
        doctor = get_object_or_404(Doctor, pk=pk)
        
        # Get and validate date parameter
        date_str = request.query_params.get('date')
        
        if not date_str:
            return Response(
                {
                    'error': 'Missing required parameter',
                    'detail': "Required parameter 'date' is missing. Please provide a date in YYYY-MM-DD format.",
                    'example': f'/api/doctors/{pk}/availability/?date=2026-07-15'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse date
        try:
            requested_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {
                    'error': 'Invalid date format',
                    'detail': f"Date '{date_str}' is not in valid format. Please use YYYY-MM-DD format.",
                    'example': '2026-07-15',
                    'provided': date_str
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate availability
        try:
            availability_data = AvailabilityService.calculate_available_slots(
                doctor, requested_date
            )
            
            # Serialize and return
            serializer = AvailabilityResponseSerializer(availability_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {
                    'error': 'Validation error',
                    'detail': str(e.message) if hasattr(e, 'message') else str(e),
                    'doctor': f"Dr. {doctor.full_name}",
                    'requested_date': date_str
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'detail': 'An unexpected error occurred while calculating availability. Please try again or contact support.',
                    'technical_detail': str(e) if request.user and request.user.is_staff else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
