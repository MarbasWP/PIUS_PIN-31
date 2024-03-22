from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import (filters, mixins, permissions, status, views,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User

from .permissions import IsAdmin
from .serializers import (AuthSignupSerializer, GetJWTTokenSerializer, UserViewSerializer)


class AuthSignupView(views.APIView):
    """Класс для регистрации новых пользователей."""

    def post(self, request):
        username_and_email_exists = User.objects.filter(
            username=request.data.get("username"),
            email=request.data.get("email"),
        ).exists()
        if username_and_email_exists:
            return Response({'detail': 'Пользователь с таким username и email уже существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = AuthSignupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.create_user(
                username=serializer.validated_data.get("username"),
                email=serializer.validated_data.get("email"),
            )
            secret_code = User.objects.make_random_password()
            user.set_password(secret_code)
            user.save()
            return Response(
                {
                    'username': user.username,
                    'email': user.email,
                    'secret_code': secret_code,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetJWTTokenView(views.APIView):
    """
    Класс для получения JWT токена в обмен
    на username и confirmation code.
    """

    def post(self, request):
        serializer = GetJWTTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, username=serializer.data.get("username"))
        if not user.check_password(serializer.data.get("confirmation_code")):
            return Response({"detail": "Ошибка: не верный confirmation_code"}, status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        return Response(
            {"token": str(refresh.access_token)},
            status=status.HTTP_201_CREATED,
        )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserViewSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"

    def update(self, request, *args, **kwargs):
        if request.method in "PUT":
            return Response(
                request.data, status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(
        methods=["get", "patch"],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if request.user.is_admin:
            serializer.save()
        else:
            serializer.save(role=self.request.user.role)

        return Response(serializer.data, status=status.HTTP_200_OK)
