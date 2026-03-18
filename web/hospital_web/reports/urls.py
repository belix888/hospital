from django.urls import path

from . import views


urlpatterns = [
    path("", views.reports_home, name="reports_home"),
    path("create/", views.reports_create, name="reports_create"),
    path("list/", views.reports_list_partial, name="reports_list_partial"),
]

