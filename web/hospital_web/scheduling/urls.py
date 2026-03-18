from django.urls import path

from . import views


urlpatterns = [
    path("", views.my_appointments, name="my_appointments"),
    path("create/", views.appointment_create, name="appointment_create"),
    path("patients/quick-add/", views.patient_quick_add, name="patient_quick_add"),
    path("available-rooms/", views.available_rooms_partial, name="available_rooms_partial"),
    path("calendar/", views.calendar_month, name="calendar_month"),
    path("day/", views.day_view, name="day_view"),
]

