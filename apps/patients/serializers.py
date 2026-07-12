from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model."""
    
    full_name = serializers.CharField(read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'date_of_birth',
            'age',
            'gender',
            'email',
            'phone',
            'address',
            'emergency_contact_name',
            'emergency_contact_phone',
            'medical_history',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_age(self, obj):
        """Calculate patient's age."""
        from datetime import date
        today = date.today()
        return today.year - obj.date_of_birth.year - (
            (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
        )
