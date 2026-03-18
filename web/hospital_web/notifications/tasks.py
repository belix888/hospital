from __future__ import annotations

from datetime import datetime, timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from scheduling.models import Appointment, AppointmentStatus


def _doctor_emails(appt: Appointment) -> list[str]:
    emails: list[str] = []
    if appt.doctor.email:
        emails.append(appt.doctor.email)
    u = getattr(appt.doctor, "user", None)
    if u and getattr(u, "email", ""):
        emails.append(u.email)
    return list(dict.fromkeys([e for e in emails if e]))


@shared_task
def scan_and_send_notifications() -> dict:
    """
    Periodic task (every minute):
    - sends extension prompt 15 minutes before end (once)
    - sends completion notification at/after end (once)
    """
    now = timezone.localtime(timezone.now())
    window_end = now + timedelta(minutes=15)

    # Consider appointments from today and adjacent day to avoid timezone edge cases
    date_min = (now - timedelta(days=1)).date()
    date_max = (now + timedelta(days=1)).date()

    qs = (
        Appointment.objects.select_related("doctor", "room")
        .filter(
            appointment_date__gte=date_min,
            appointment_date__lte=date_max,
            status=AppointmentStatus.SCHEDULED,
        )
        .only(
            "id",
            "appointment_date",
            "appointment_time",
            "duration_minutes",
            "extension_prompt_sent_at",
            "completion_sent_at",
            "doctor__id",
            "doctor__name",
            "doctor__email",
            "doctor__user_id",
            "room__name",
        )
    )

    extension_sent = 0
    completion_sent = 0

    for appt in qs:
        start = datetime.combine(appt.appointment_date, appt.appointment_time)
        end = start + timedelta(minutes=int(appt.duration_minutes))

        # Extension prompt
        remind_at = end - timedelta(minutes=15)
        if appt.extension_prompt_sent_at is None and remind_at <= now <= end:
            emails = _doctor_emails(appt)
            if emails:
                send_mail(
                    subject="Приём заканчивается через 15 минут — продлить?",
                    message=(
                        f"Кабинет: {appt.room.name}\n"
                        f"Окончание: {end.strftime('%H:%M')}\n\n"
                        f"Откройте сайт, чтобы продлить или завершить приём."
                    ),
                    from_email=None,
                    recipient_list=emails,
                    fail_silently=True,
                )
            Appointment.objects.filter(id=appt.id, extension_prompt_sent_at__isnull=True).update(
                extension_prompt_sent_at=timezone.now()
            )
            extension_sent += 1

        # Completion notification
        if appt.completion_sent_at is None and end <= now:
            emails = _doctor_emails(appt)
            if emails:
                send_mail(
                    subject="Приём завершён",
                    message=(
                        f"Кабинет: {appt.room.name}\n"
                        f"Время окончания: {end.strftime('%H:%M')}\n"
                    ),
                    from_email=None,
                    recipient_list=emails,
                    fail_silently=True,
                )
            Appointment.objects.filter(id=appt.id, completion_sent_at__isnull=True).update(completion_sent_at=timezone.now())
            completion_sent += 1

    return {"extension_sent": extension_sent, "completion_sent": completion_sent}

