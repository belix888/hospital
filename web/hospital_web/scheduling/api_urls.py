from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import AppointmentViewSet, AvailableRoomsView, RoomMonitorView


router = DefaultRouter()
router.register(r"appointments", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("", include(router.urls)),
    path("rooms/monitor/", RoomMonitorView.as_view(), name="api_room_monitor"),
    path("rooms/available/", AvailableRoomsView.as_view(), name="api_available_rooms"),
]

