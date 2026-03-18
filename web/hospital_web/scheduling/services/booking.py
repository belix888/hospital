from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from django.db import transaction

from clinic.models import Doctor, Patient, Room
from scheduling.models import Appointment, AppointmentStatus


@dataclass(frozen=True)
class Conflict:
    appointment: Appointment
    existing_start: datetime
    existing_end: datetime


def _intervals_intersect(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def find_room_conflict(
    *,
    room: Room,
    appointment_date,
    appointment_time,
    duration_minutes: int,
    exclude_appointment_id: int | None = None,
) -> Optional[Conflict]:
    """
    Port of DatabaseManager.find_room_conflict() from the bot version,
    but using ORM and returning a richer object.
    """
    new_start = datetime.combine(appointment_date, appointment_time)
    new_end = new_start + timedelta(minutes=int(duration_minutes))

    qs = Appointment.objects.select_related("doctor", "room").filter(
        room=room,
        appointment_date=appointment_date,
        status=AppointmentStatus.SCHEDULED,
    )
    if exclude_appointment_id:
        qs = qs.exclude(id=exclude_appointment_id)

    for a in qs.order_by("appointment_time"):
        exist_start = datetime.combine(a.appointment_date, a.appointment_time)
        exist_end = exist_start + timedelta(minutes=int(a.duration_minutes))
        if _intervals_intersect(new_start, new_end, exist_start, exist_end):
            return Conflict(appointment=a, existing_start=exist_start, existing_end=exist_end)
    return None


def get_available_rooms(*, appointment_date, appointment_time, duration_minutes: int) -> list[Room]:
    """
    Port of DatabaseManager.get_available_rooms() from the bot version.
    """
    new_start = datetime.combine(appointment_date, appointment_time)
    new_end = new_start + timedelta(minutes=int(duration_minutes))

    rooms = list(Room.objects.filter(is_available=True, is_deleted=False).order_by("name"))
    occupied_room_ids: set[int] = set()

    qs = Appointment.objects.select_related("room").filter(
        appointment_date=appointment_date,
        status=AppointmentStatus.SCHEDULED,
    )
    for a in qs:
        exist_start = datetime.combine(a.appointment_date, a.appointment_time)
        exist_end = exist_start + timedelta(minutes=int(a.duration_minutes))
        if _intervals_intersect(new_start, new_end, exist_start, exist_end):
            occupied_room_ids.add(a.room_id)

    return [r for r in rooms if r.id not in occupied_room_ids]


@transaction.atomic
def create_appointment(
    *,
    doctor: Doctor,
    patient: Patient,
    room: Room,
    appointment_date,
    appointment_time,
    duration_minutes: int,
    notes: str = "",
) -> Appointment:
    """
    Safe appointment creation with conflict re-check under a transaction.
    """
    # Lock scheduled appointments for the same room+date to prevent race conditions.
    (
        Appointment.objects.select_for_update()
        .filter(room=room, appointment_date=appointment_date, status=AppointmentStatus.SCHEDULED)
        .only("id")
    )

    conflict = find_room_conflict(
        room=room,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        duration_minutes=duration_minutes,
    )
    if conflict:
        raise ValueError(
            f"Room conflict: {room.name} intersects with appointment #{conflict.appointment.id} "
            f"({conflict.existing_start.strftime('%H:%M')}-{conflict.existing_end.strftime('%H:%M')})"
        )

    return Appointment.objects.create(
        doctor=doctor,
        patient=patient,
        room=room,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        duration_minutes=int(duration_minutes),
        status=AppointmentStatus.SCHEDULED,
        notes=notes or "",
    )


@transaction.atomic
def can_extend_appointment(*, appointment: Appointment, extra_minutes: int) -> bool:
    """
    Port of DatabaseManager.can_extend_appointment():
    checks whether the tail [old_end, new_end) intersects other scheduled appointments in the same room/date.
    """
    if extra_minutes <= 0:
        return False

    # Lock candidates to prevent concurrent modifications
    (
        Appointment.objects.select_for_update()
        .filter(room=appointment.room, appointment_date=appointment.appointment_date, status=AppointmentStatus.SCHEDULED)
        .only("id")
    )

    start = datetime.combine(appointment.appointment_date, appointment.appointment_time)
    old_end = start + timedelta(minutes=int(appointment.duration_minutes))
    new_end = old_end + timedelta(minutes=int(extra_minutes))

    qs = Appointment.objects.filter(
        room=appointment.room,
        appointment_date=appointment.appointment_date,
        status=AppointmentStatus.SCHEDULED,
    ).exclude(id=appointment.id)

    for a in qs:
        exist_start = datetime.combine(a.appointment_date, a.appointment_time)
        exist_end = exist_start + timedelta(minutes=int(a.duration_minutes))
        if _intervals_intersect(old_end, new_end, exist_start, exist_end):
            return False
    return True


@transaction.atomic
def extend_appointment(*, appointment_id: int, extra_minutes: int) -> Appointment:
    appointment = (
        Appointment.objects.select_for_update()
        .select_related("room", "doctor")
        .get(id=appointment_id)
    )
    if appointment.status != AppointmentStatus.SCHEDULED:
        raise ValueError("Appointment is not scheduled")

    if not can_extend_appointment(appointment=appointment, extra_minutes=extra_minutes):
        raise ValueError("Cannot extend: conflicts with another appointment")

    appointment.duration_minutes = int(appointment.duration_minutes) + int(extra_minutes)
    appointment.save(update_fields=["duration_minutes"])
    return appointment


@transaction.atomic
def finish_appointment_now(*, appointment_id: int, finished_at: datetime | None = None) -> Appointment:
    """
    Web analog of /finish: mark as completed and adjust duration to elapsed minutes.
    """
    finished_at = finished_at or datetime.now()
    appointment = Appointment.objects.select_for_update().get(id=appointment_id)
    if appointment.status != AppointmentStatus.SCHEDULED:
        raise ValueError("Appointment is not scheduled")

    start = datetime.combine(appointment.appointment_date, appointment.appointment_time)
    elapsed = max(1, int((finished_at - start).total_seconds() // 60))
    appointment.duration_minutes = min(int(appointment.duration_minutes), elapsed)
    appointment.status = AppointmentStatus.COMPLETED
    appointment.save(update_fields=["duration_minutes", "status"])
    return appointment

