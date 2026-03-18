from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from scheduling.services.monitoring import build_room_monitoring_view


@login_required
def dashboard(request):
    return render(request, "clinic/dashboard.html", {})


@login_required
def room_monitor(request):
    date_str = request.GET.get("date") or datetime.now().strftime("%Y-%m-%d")
    vm = build_room_monitoring_view(date_str=date_str)
    template = "clinic/partials/room_monitor.html" if request.htmx else "clinic/room_monitor.html"
    return render(request, template, vm)
