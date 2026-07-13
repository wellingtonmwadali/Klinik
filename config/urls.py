"""URL Configuration for Klinik project."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint for Render deployment verification."""
    return JsonResponse({'status': 'healthy', 'service': 'klinik-api'})

def home(request):
    return JsonResponse({
        "message": "Clinic Booking API",
        "status": "running"
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    path('api/appointments/', include('apps.appointments.urls')),
    path('api/doctors/', include('apps.doctors.urls')),
    path('api/patients/', include('apps.patients.urls')),
    path('', home, name='home'),
]

# Add debug toolbar URLs in development
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
