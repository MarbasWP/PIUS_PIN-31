from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, ScheduleView

app_name = "api"

router_v1 = DefaultRouter()
router_v1.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("v1/", include(router_v1.urls)),
    path('v1/events/', ScheduleView.as_view(), name='events'),
    path('v1/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
