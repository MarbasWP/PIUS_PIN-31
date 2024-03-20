from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AuthSignupView, GetJWTTokenView,  UsersViewSet)

app_name = "api"

router_v1 = DefaultRouter()
router_v1.register(r"users", UsersViewSet, basename="users")

urlpatterns = [
    path("v1/auth/signup/", AuthSignupView.as_view()),
    path("v1/auth/token/", GetJWTTokenView.as_view()),
    path("v1/", include(router_v1.urls)),
]
