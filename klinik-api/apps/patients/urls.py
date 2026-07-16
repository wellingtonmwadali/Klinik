from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PatientRegistrationView, PatientViewSet

router = DefaultRouter()
router.register(r"", PatientViewSet, basename="patient")

urlpatterns = [
    # Register a new patient
    path(
        "register/",
        PatientRegistrationView.as_view(),
        name="patient-register",
    ),

    # Existing CRUD endpoints
    path("", include(router.urls)),
]