from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from clinic.models import Doctor, Patient, Room
from scheduling.forms import AppointmentCreateForm
from scheduling.patient_forms import PatientQuickAddForm
from scheduling.models import Appointment, AppointmentStatus
from scheduling.services.booking import get_available_rooms


def _current_doctor(request: HttpRequest) -> Doctor | None:
    # Prefer profile attached to user; fallback for staff users to view all
    if hasattr(request.user, "doctor_profile"):
        return request.user.doctor_profile
    return None


@login_required
def my_appointments(request: HttpRequest) -> HttpResponse:
    doctor = _current_doctor(request)
    qs = Appointment.objects.select_related("doctor", "patient", "room")
    if doctor:
        qs = qs.filter(doctor=doctor)
    qs = qs.order_by("-appointment_date", "-appointment_time")[:200]
    return render(request, "scheduling/my_appointments.html", {"appointments": qs, "doctor": doctor})


@login_required
def appointment_create(request: HttpRequest) -> HttpResponse:
    doctor = _current_doctor(request)
    if request.method == "POST":
        form = AppointmentCreateForm(request.POST, doctor=doctor)
        if form.is_valid():
            form.save()
            return redirect("my_appointments")
    else:
        form = AppointmentCreateForm(doctor=doctor)

    patients = Patient.objects.order_by("name", "id")
    return render(
        request,
        "scheduling/appointment_create.html",
        {"form": form, "doctor": doctor, "patients": patients},
    )


@login_required
def patient_quick_add(request: HttpRequest) -> HttpResponse:
    """
    HTMX: create Patient without leaving appointment form.
    GET  -> returns mini-form
    POST -> creates patient, returns refreshed patient selector (selected new)
    """
    if request.GET.get("close") == "1":
        return HttpResponse("")

    if request.method == "POST":
        form = PatientQuickAddForm(request.POST)
        if form.is_valid():
            p = form.save()
            patients = Patient.objects.order_by("name", "id")
            return render(
                request,
                "scheduling/partials/patient_field.html",
                {"patients": patients, "selected_patient_id": p.id},
            )
        return render(request, "scheduling/partials/patient_quick_add_form.html", {"pform": form}, status=400)

    form = PatientQuickAddForm()
    return render(request, "scheduling/partials/patient_quick_add_form.html", {"pform": form})


@login_required
def available_rooms_partial(request: HttpRequest) -> HttpResponse:
    """
    HTMX endpoint: given date/time/duration, returns <option> list of available rooms.
    """
    try:
        d = request.GET.get("appointment_date") or ""
        t = request.GET.get("appointment_time") or ""
        duration = int(request.GET.get("duration_minutes") or 60)
        if not d or not t:
            return render(request, "scheduling/partials/available_rooms_options.html", {"rooms": []})
        appointment_date = datetime.strptime(d, "%Y-%m-%d").date()
        appointment_time = datetime.strptime(t, "%H:%M").time()
    except Exception:
        return render(request, "scheduling/partials/available_rooms_options.html", {"rooms": []})

    rooms = get_available_rooms(appointment_date=appointment_date, appointment_time=appointment_time, duration_minutes=duration)
    return render(request, "scheduling/partials/available_rooms_options.html", {"rooms": rooms})


@login_required
def day_view(request: HttpRequest) -> HttpResponse:
    """
    Simple day view for all doctors/rooms (like bot calendar day screen).
    """
    date_str = request.GET.get("date") or date.today().strftime("%Y-%m-%d")
    target = datetime.strptime(date_str, "%Y-%m-%d").date()
    qs = (
        Appointment.objects.select_related("doctor", "patient", "room")
        .filter(appointment_date=target, status=AppointmentStatus.SCHEDULED)
        .order_by("room__name", "appointment_time")
    )
    rooms = list(Room.objects.order_by("name"))
    return render(request, "scheduling/day_view.html", {"date_str": date_str, "appointments": qs, "rooms": rooms})


@login_required
def calendar_month(request: HttpRequest) -> HttpResponse:
    """
    Month grid with navigation, similar to bot inline calendar.
    """
    today = date.today()
    year = int(request.GET.get("year") or today.year)
    month = int(request.GET.get("month") or today.month)

    first_day = date(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)  # weekday, days

    # Build list of weeks (Mon..Sun)
    start_weekday_mon0 = (first_day.weekday())  # 0..6 (Mon..Sun)
    weeks: list[list[dict]] = []
    week: list[dict] = []

    for _ in range(start_weekday_mon0):
        week.append({"day": None, "date_str": None})

    # Precompute which dates have appointments (scheduled) for fast highlighting
    start = first_day
    end = first_day + timedelta(days=days_in_month)
    appt_dates = set(
        Appointment.objects.filter(
            appointment_date__gte=start,
            appointment_date__lt=end,
            status=AppointmentStatus.SCHEDULED,
        ).values_list("appointment_date", flat=True)
    )

    for d in range(1, days_in_month + 1):
        dt = date(year, month, d)
        week.append(
            {
                "day": d,
                "date_str": dt.strftime("%Y-%m-%d"),
                "is_today": dt == today,
                "has_appointments": dt in appt_dates,
            }
        )
        if len(week) == 7:
            weeks.append(week)
            week = []

    if week:
        while len(week) < 7:
            week.append({"day": None, "date_str": None})
        weeks.append(week)

    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)

    return render(
        request,
        "scheduling/calendar_month.html",
        {
            "year": year,
            "month": month,
            "weeks": weeks,
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month,
        },
    )
