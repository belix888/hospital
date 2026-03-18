from __future__ import annotations

from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from reports.models import ReportJob, ReportKind
from reports.services.excel import export_all_doctors_month, export_doctor_month
from scheduling.models import Appointment, AppointmentStatus


def _latest_jobs_for_user(user, limit: int = 20):
    qs = ReportJob.objects.order_by("-created_at")
    if user.is_staff or user.is_superuser:
        return qs[:limit]
    return qs.filter(requested_by=user)[:limit]


@login_required
def reports_home(request: HttpRequest) -> HttpResponse:
    today = timezone.localdate()
    jobs = _latest_jobs_for_user(request.user, limit=20)
    return render(
        request,
        "reports/home.html",
        {
            "default_year": today.year,
            "default_month": today.month,
            "jobs": jobs,
            "is_staff": request.user.is_staff or request.user.is_superuser,
        },
    )


@login_required
def reports_list_partial(request: HttpRequest) -> HttpResponse:
    jobs = _latest_jobs_for_user(request.user, limit=30)
    return render(request, "reports/partials/jobs_list.html", {"jobs": jobs})


@login_required
def reports_create(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return redirect("reports_home")

    kind = request.POST.get("kind") or ""
    year = int(request.POST.get("year") or 0)
    month = int(request.POST.get("month") or 0)

    u = request.user
    params = {"year": year, "month": month}

    if kind == ReportKind.DOCTOR_MONTH:
        if not hasattr(u, "doctor_profile"):
            return HttpResponse("Требуется профиль врача", status=400)
        params["doctor_id"] = u.doctor_profile.id
    elif kind == ReportKind.ALL_DOCTORS_MONTH:
        if not (u.is_staff or u.is_superuser):
            return HttpResponse("Недостаточно прав", status=403)
    else:
        return HttpResponse("Неизвестный тип отчёта", status=400)

    # Generate synchronously and return as a downloadable file.
    appt_qs = (
        Appointment.objects.select_related("doctor", "patient", "room")
        .filter(
            status=AppointmentStatus.SCHEDULED,
            appointment_date__gte=f"{year}-{month:02d}-01",
            appointment_date__lt=f"{year + (1 if month == 12 else 0)}-{(1 if month == 12 else month + 1):02d}-01",
        )
        .order_by("appointment_date", "appointment_time", "doctor__name")
    )

    if kind == ReportKind.DOCTOR_MONTH:
        doctor = u.doctor_profile
        appts = appt_qs.filter(doctor=doctor)
        content = export_doctor_month(
            doctor_name=doctor.name,
            specialization=doctor.specialization,
            year=year,
            month=month,
            appointments=appts,
        )
        filename = f"appointments_{doctor.name.replace(' ', '_')}_{year}_{month:02d}.xlsx"
    else:
        content = export_all_doctors_month(year=year, month=month, appointments=appt_qs)
        filename = f"all_appointments_{year}_{month:02d}.xlsx"

    resp = HttpResponse(
        content,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp
