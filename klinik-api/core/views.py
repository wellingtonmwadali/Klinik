from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import LoginSerializer


def _user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role.name if user.role else None,
        "is_staff": user.is_staff,
    }


@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_view(request):
    """Ensures a csrftoken cookie is set on the response.

    Session auth's CSRF check only ever inspects a cookie that already exists on
    the request; nothing sets it until something calls get_token(). login_view
    already does this as part of login, so this is only needed if a client's
    csrftoken cookie has gone missing/expired independently of its session.
    """
    get_token(request)
    return Response({"detail": "CSRF cookie set."})


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        request,
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if user is None:
        return Response(
            {"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED
        )
    if not user.is_active:
        return Response(
            {"detail": "This account is inactive."}, status=status.HTTP_403_FORBIDDEN
        )

    login(request, user)
    # Ensure the csrftoken cookie is (re-)issued alongside the new session, since
    # subsequent authenticated mutating requests will need to send it back.
    get_token(request)
    return Response(_user_payload(user))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({"detail": "Logged out."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(_user_payload(request.user))
