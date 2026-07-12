from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Doctor
from .serializers import DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing doctors."""
    
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'is_active']
    search_fields = ['first_name', 'last_name', 'specialization', 'email']
    ordering_fields = ['last_name', 'created_at']
