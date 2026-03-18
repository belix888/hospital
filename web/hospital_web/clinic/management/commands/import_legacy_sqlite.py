from __future__ import annotations

import sqlite3
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from clinic.models import Doctor, Patient, Room
from scheduling.models import Appointment, AppointmentStatus


class Command(BaseCommand):
    help = "Imports legacy SQLite data from hospital_bot.db into Django models."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sqlite-path",
            default=str(Path(__file__).resolve().parents[5] / "hospital_bot.db"),
            help="Path to legacy hospital_bot.db (SQLite)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate, but do not write to DB",
        )

    def handle(self, *args, **options):
        sqlite_path = Path(options["sqlite_path"])
        dry_run = bool(options["dry_run"])

        if not sqlite_path.exists():
            raise CommandError(f"SQLite file not found: {sqlite_path}")

        self.stdout.write(f"Reading legacy DB: {sqlite_path}")

        with sqlite3.connect(str(sqlite_path)) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute("SELECT * FROM doctors ORDER BY id")
            legacy_doctors = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT * FROM patients ORDER BY id")
            legacy_patients = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT * FROM appointments ORDER BY id")
            legacy_appointments = [dict(r) for r in cur.fetchall()]

        self.stdout.write(
            f"Found: doctors={len(legacy_doctors)}, patients={len(legacy_patients)}, appointments={len(legacy_appointments)}"
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run mode: no writes will be performed."))
            return

        with transaction.atomic():
            # Doctors
            doctor_map: dict[int, Doctor] = {}
            for d in legacy_doctors:
                obj, _ = Doctor.objects.get_or_create(
                    telegram_id=d.get("telegram_id"),
                    defaults={
                        "name": d.get("name") or "Unknown",
                        "specialization": d.get("specialization") or "",
                        "phone": d.get("phone") or "",
                        "email": d.get("email") or "",
                        "is_active": bool(d.get("is_active", 1)),
                    },
                )
                # If existing, update basic fields (keep user link)
                obj.name = d.get("name") or obj.name
                obj.specialization = d.get("specialization") or obj.specialization
                obj.phone = d.get("phone") or obj.phone
                obj.email = d.get("email") or obj.email
                obj.is_active = bool(d.get("is_active", 1))
                obj.save()
                doctor_map[int(d["id"])] = obj

            # Patients
            patient_map: dict[int, Patient] = {}
            for p in legacy_patients:
                # Dedup by phone+name
                obj, _ = Patient.objects.get_or_create(
                    phone=p.get("phone") or "",
                    name=p.get("name") or "Unknown",
                    defaults={"birth_date": p.get("birth_date") or None},
                )
                patient_map[int(p["id"])] = obj

            # Rooms by name
            room_map: dict[str, Room] = {}

            def get_room(name: str) -> Room:
                key = (name or "").strip() or "Unknown"
                if key in room_map:
                    return room_map[key]
                obj, _ = Room.objects.get_or_create(name=key, defaults={"is_available": True})
                room_map[key] = obj
                return obj

            # Appointments
            created = 0
            skipped = 0
            for a in legacy_appointments:
                doctor = doctor_map.get(int(a["doctor_id"]))
                patient = patient_map.get(int(a["patient_id"]))
                if not doctor or not patient:
                    skipped += 1
                    continue
                room = get_room(a.get("room") or "")

                status = a.get("status") or AppointmentStatus.SCHEDULED
                if status not in {AppointmentStatus.SCHEDULED, AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED}:
                    status = AppointmentStatus.SCHEDULED

                # Avoid duplicates on same tuple
                obj, was_created = Appointment.objects.get_or_create(
                    doctor=doctor,
                    patient=patient,
                    room=room,
                    appointment_date=a.get("appointment_date"),
                    appointment_time=a.get("appointment_time"),
                    defaults={
                        "duration_minutes": int(a.get("duration") or 60),
                        "status": status,
                        "notes": a.get("notes") or "",
                    },
                )
                if was_created:
                    created += 1
                else:
                    # Update existing with latest info
                    obj.duration_minutes = int(a.get("duration") or obj.duration_minutes)
                    obj.status = status
                    obj.notes = a.get("notes") or obj.notes
                    obj.save()

            self.stdout.write(self.style.SUCCESS(f"Imported appointments: created={created}, skipped={skipped}"))

