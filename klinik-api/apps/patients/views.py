from urllib import response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Patient
from .serializers import PatientRegistrationSerializer, PatientSerializer

class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet for managing patients."""

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [ "is_active"]
    search_fields = ["first_name", "last_name", "email", "phone"]
    ordering_fields = ["last_name", "created_at"]

class PatientRegistrationView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = PatientRegistrationSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Patient registered successfully."
            },
            status=status.HTTP_201_CREATED,
        )