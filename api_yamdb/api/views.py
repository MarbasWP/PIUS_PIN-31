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

EMAIL_TITLE = "Приветствуем {}"
EMAIL_MESSAGE = "Ваш секретный код: {}"


class MyMixinsSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class AuthSignupView(views.APIView):
    """Класс для регистрации новых пользователей."""

    def post(self, request):
        username_and_email_exists = User.objects.filter(
            username=request.data.get("username"),
            email=request.data.get("email"),
        ).exists()
        if username_and_email_exists:
            return Response(request.data, status=status.HTTP_200_OK)
        serializer = AuthSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(
            serializer.data.get("username"),
            email=serializer.data.get("email"),
        )
        send_mail(
            EMAIL_TITLE.format(serializer.data.get("username")),
            EMAIL_MESSAGE.format(user.password),
            settings.ADMINS_EMAIL,
            [serializer.data.get("email")],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetJWTTokenView(views.APIView):
    """
    Класс для получения JWT токена в обмен
    на username и confirmation code.
    """

    def post(self, request):
        serializer = GetJWTTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, password=serializer.data.get("confirmation_code")
        )
        refresh = RefreshToken.for_user(user)

        return Response(
            {"token": str(refresh.access_token)},
            status=status.HTTP_201_CREATED,
        )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserViewSerializer
    permission_classes = (IsAdmin, permissions.IsAuthenticated)
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

        # если пользователь admin, то можно менять поле role,
        # в остальных случаях нельзя
        if request.user.is_admin:
            serializer.save()
        else:
            serializer.save(role=self.request.user.role)

        return Response(serializer.data, status=status.HTTP_200_OK)
