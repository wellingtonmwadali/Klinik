from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model."""
    
    full_name = serializers.CharField(read_only=True)
    appointment_count = serializers.IntegerField(
        source='appointments.count',
        read_only=True
    )

    class Meta:
        model = Doctor
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'specialization',
            'license_number',
            'is_active',
            'bio',
            'appointment_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
