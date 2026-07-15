from rest_framework import serializers
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Patient
from core.models import Role
User = get_user_model()

class PatientSerializer(serializers.ModelSerializer):
    """Serializer for returning patient information."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]



class PatientRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    def validate_phone(self, value):
        if Patient.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "Phone number is already registered."
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "confirm_password": "Passwords do not match."
                }
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("confirm_password")

        patient_role = Role.objects.filter(name=Role.PATIENT).first()

        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=password,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data["phone"],
            role=patient_role,
        )

        patient = Patient.objects.create(
            user=user,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            phone=validated_data["phone"],
        )

        return patient