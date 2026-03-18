from __future__ import annotations

import os
from datetime import datetime

from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone

from clinic.models import Doctor
from reports.models import ReportJob, ReportKind, ReportStatus
from reports.services.excel import export_all_doctors_month, export_doctor_month
from scheduling.models import Appointment, AppointmentStatus


@shared_task
def generate_report_job(report_job_id: int) -> None:
    job = ReportJob.objects.get(id=report_job_id)
    try:
        kind = job.kind
        year = int(job.params.get("year"))
        month = int(job.params.get("month"))

        if kind == ReportKind.DOCTOR_MONTH:
            doctor_id = int(job.params.get("doctor_id"))
            doctor = Doctor.objects.get(id=doctor_id)
            appts = (
                Appointment.objects.select_related("doctor", "patient", "room")
                .filter(
                    doctor=doctor,
                    status=AppointmentStatus.SCHEDULED,
                    appointment_date__gte=f"{year}-{month:02d}-01",
                    appointment_date__lt=f"{year + (1 if month == 12 else 0)}-{(1 if month == 12 else month + 1):02d}-01",
                )
                .order_by("appointment_date", "appointment_time")
            )
            content = export_doctor_month(
                doctor_name=doctor.name,
                specialization=doctor.specialization,
                year=year,
                month=month,
                appointments=appts,
            )
            filename = f"appointments_{doctor.name.replace(' ', '_')}_{year}_{month:02d}.xlsx"

        elif kind == ReportKind.ALL_DOCTORS_MONTH:
            appts = (
                Appointment.objects.select_related("doctor", "patient", "room")
                .filter(
                    status=AppointmentStatus.SCHEDULED,
                    appointment_date__gte=f"{year}-{month:02d}-01",
                    appointment_date__lt=f"{year + (1 if month == 12 else 0)}-{(1 if month == 12 else month + 1):02d}-01",
                )
                .order_by("appointment_date", "appointment_time", "doctor__name")
            )
            content = export_all_doctors_month(year=year, month=month, appointments=appts)
            filename = f"all_appointments_{year}_{month:02d}.xlsx"
        else:
            raise ValueError(f"Unknown report kind: {kind}")

        job.file.save(filename, ContentFile(content), save=False)
        job.status = ReportStatus.DONE
        job.finished_at = timezone.now()
        job.error = ""
        job.save()
    except Exception as e:
        job.status = ReportStatus.FAILED
        job.finished_at = timezone.now()
        job.error = str(e)
        job.save()

