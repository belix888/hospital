from __future__ import annotations

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Deletes all domain data and keeps only the specified admin account."

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-username",
            default="admin",
            help="Username to keep (superuser/admin). All other users will be deleted.",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Actually perform deletion. Without this flag, runs in dry-run mode.",
        )

    def handle(self, *args, **options):
        keep_username: str = options["keep_username"]
        do_it: bool = bool(options["yes"])

        User = get_user_model()
        try:
            keep_user = User.objects.get(username=keep_username)
        except User.DoesNotExist:
            raise CommandError(f"User '{keep_username}' not found.")

        # Models to wipe (order matters due to FK protections)
        Appointment = apps.get_model("scheduling", "Appointment")
        ReportJob = apps.get_model("reports", "ReportJob")
        Doctor = apps.get_model("clinic", "Doctor")
        Patient = apps.get_model("clinic", "Patient")
        Room = apps.get_model("clinic", "Room")

        LogEntry = apps.get_model("admin", "LogEntry")
        Session = apps.get_model("sessions", "Session")
        Group = apps.get_model("auth", "Group")

        counts = {
            "appointments": Appointment.objects.count(),
            "report_jobs": ReportJob.objects.count(),
            "doctors": Doctor.objects.count(),
            "patients": Patient.objects.count(),
            "rooms": Room.objects.count(),
            "admin_log": LogEntry.objects.count(),
            "sessions": Session.objects.count(),
            "groups": Group.objects.count(),
            "users_to_delete": User.objects.exclude(id=keep_user.id).count(),
        }

        self.stdout.write("Planned cleanup:")
        for k, v in counts.items():
            self.stdout.write(f"- {k}: {v}")

        if not do_it:
            self.stdout.write(self.style.WARNING("Dry-run mode. Re-run with --yes to apply."))
            return

        with transaction.atomic():
            # Domain data
            Appointment.objects.all().delete()
            ReportJob.objects.all().delete()
            Doctor.objects.all().delete()
            Patient.objects.all().delete()
            Room.objects.all().delete()

            # Auth/supporting tables
            LogEntry.objects.all().delete()
            Session.objects.all().delete()
            Group.objects.all().delete()

            # Users except kept admin
            User.objects.exclude(id=keep_user.id).delete()

            # Ensure kept user is admin
            keep_user.is_active = True
            keep_user.is_staff = True
            keep_user.is_superuser = True
            keep_user.save(update_fields=["is_active", "is_staff", "is_superuser"])

        self.stdout.write(self.style.SUCCESS("Cleanup completed."))

