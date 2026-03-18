from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from clinic.models import Room
from scheduling.models import Appointment, AppointmentStatus


@dataclass(frozen=True)
class RoomLine:
    room_id: int
    room_name: str
    is_busy_now: bool
    busy_until: str | None
    current_doctor_name: str | None
    upcoming_time: str | None
    upcoming_doctor_name: str | None


def build_room_monitoring_view(*, date_str: str) -> dict[str, Any]:
    """
    Web analog of bot.py build_room_monitoring_view():
    shows current room occupancy and next appointment for a given date.
    """
    now = datetime.now()
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    rooms = list(Room.objects.filter(is_deleted=False).order_by("name"))
    appts = (
        Appointment.objects.select_related("doctor", "room")
        .filter(appointment_date=target_date, status=AppointmentStatus.SCHEDULED)
        .order_by("appointment_time")
    )

    by_room: dict[int, list[Appointment]] = {}
    for a in appts:
        by_room.setdefault(a.room_id, []).append(a)

    lines: list[RoomLine] = []
    for room in rooms:
        items = by_room.get(room.id, [])
        current: tuple[Appointment, datetime] | None = None
        upcoming: Appointment | None = None

        for a in items:
            start = datetime.combine(a.appointment_date, a.appointment_time)
            end = start + timedelta(minutes=int(a.duration_minutes))
            if start <= now < end:
                current = (a, end)
            if start > now and upcoming is None:
                upcoming = a

        if current:
            a, end = current
            lines.append(
                RoomLine(
                    room_id=room.id,
                    room_name=room.name,
                    is_busy_now=True,
                    busy_until=end.strftime("%H:%M"),
                    current_doctor_name=a.doctor.name,
                    upcoming_time=upcoming.appointment_time.strftime("%H:%M") if upcoming else None,
                    upcoming_doctor_name=upcoming.doctor.name if upcoming else None,
                )
            )
        else:
            lines.append(
                RoomLine(
                    room_id=room.id,
                    room_name=room.name,
                    is_busy_now=False,
                    busy_until=None,
                    current_doctor_name=None,
                    upcoming_time=upcoming.appointment_time.strftime("%H:%M") if upcoming else None,
                    upcoming_doctor_name=upcoming.doctor.name if upcoming else None,
                )
            )

    return {
        "date_str": date_str,
        "lines": lines,
        "now": now,
    }

