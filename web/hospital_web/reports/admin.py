from django.contrib import admin

from .models import ReportJob


@admin.register(ReportJob)
class ReportJobAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "status", "requested_by", "created_at", "finished_at")
    list_filter = ("kind", "status", "created_at")
    search_fields = ("id", "requested_by__username")
from django.contrib import admin

# Register your models here.
