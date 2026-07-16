from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """Credentials for POST /api/auth/login/."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
