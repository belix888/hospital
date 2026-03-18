from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment_date", "appointment_time", "duration_minutes", "status", "room", "doctor", "patient")
    list_filter = ("status", "appointment_date", "room", "doctor")
    search_fields = ("doctor__name", "patient__name", "patient__phone", "room__name")
    ordering = ("-appointment_date", "-appointment_time")
