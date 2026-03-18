from datetime import datetime, timedelta

from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Doctor, Patient, Room
from scheduling.models import Appointment, AppointmentStatus


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "user_login", "name", "specialization", "phone", "email", "is_active", "created_at")
    search_fields = ("name", "specialization", "phone", "email")
    list_filter = ("is_active", "specialization")
    readonly_fields = ("user_login", "created_at")

    @admin.display(description="Логин")
    def user_login(self, obj: Doctor) -> str:
        return getattr(obj.user, "username", "") or "—"

    fieldsets = (
        (None, {"fields": ("user", "user_login", "telegram_id")}),
        ("Профиль врача", {"fields": ("name", "specialization", "phone", "email", "is_active")}),
        ("Система", {"fields": ("created_at",)}),
    )


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "birth_date", "created_at")
    search_fields = ("name", "phone")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_available", "is_deleted", "deleted_at", "last_appointment_at")
    list_filter = ("is_available", "is_deleted")
    readonly_fields = ("deleted_at", "is_deleted", "last_appointment_at")
    actions = None
    delete_confirmation_template = "admin/clinic/room/delete_confirmation.html"
    search_fields = ("name",)

    @admin.display(description="Последняя запись")
    def last_appointment_at(self, obj: Room):
        last = (
            Appointment.objects.filter(room=obj)
            .order_by("-appointment_date", "-appointment_time")
            .values_list("appointment_date", "appointment_time")
            .first()
        )
        if not last:
            return "—"
        d, t = last
        return datetime.combine(d, t).strftime("%Y-%m-%d %H:%M")

    def get_queryset(self, request):
        """
        Hide deleted rooms by default to match user expectation of "deleted = gone".
        Use ?show_deleted=1 to include deleted, or use list filter.
        """
        qs = super().get_queryset(request)
        if request.GET.get("show_deleted") == "1":
            return qs
        # If user explicitly filters by is_deleted, respect it
        if "is_deleted__exact" in request.GET:
            return qs
        return qs.filter(is_deleted=False)

    def _room_last_appt_dt(self, room: Room):
        last = (
            Appointment.objects.filter(room=room)
            .order_by("-appointment_date", "-appointment_time")
            .values_list("appointment_date", "appointment_time")
            .first()
        )
        if not last:
            return None
        d, t = last
        return datetime.combine(d, t)

    def _has_future_scheduled(self, room: Room) -> bool:
        now = timezone.localtime(timezone.now())
        today = now.date()
        qs = Appointment.objects.filter(room=room, status=AppointmentStatus.SCHEDULED)
        # Any future date
        if qs.filter(appointment_date__gt=today).exists():
            return True
        # Today but time in future
        return qs.filter(appointment_date=today, appointment_time__gt=now.time()).exists()

    def _needs_extra_confirm(self, room: Room) -> bool:
        last_dt = self._room_last_appt_dt(room)
        if not last_dt:
            return False
        return last_dt >= (timezone.localtime(timezone.now()) - timedelta(days=30)).replace(tzinfo=None)

    def delete_view(self, request, object_id, extra_context=None):
        room = self.get_object(request, object_id)
        if room is None:
            return super().delete_view(request, object_id, extra_context=extra_context)

        if room.is_deleted:
            messages.info(request, "Кабинет уже удалён (архивирован).")
            return redirect("admin:clinic_room_changelist")

        if self._has_future_scheduled(room):
            messages.error(
                request,
                "Нельзя удалить кабинет: есть будущие запланированные записи. Сначала перенесите или отмените их.",
            )
            return redirect("admin:clinic_room_change", object_id)

        extra_context = extra_context or {}
        extra_context["needs_extra_confirm"] = self._needs_extra_confirm(room)
        extra_context["last_appointment_at"] = self._room_last_appt_dt(room)
        extra_context["opts"] = self.model._meta
        extra_context["object"] = room
        extra_context["title"] = f"Удалить кабинет: {room.name}"

        if request.method == "POST":
            if extra_context["needs_extra_confirm"] and request.POST.get("extra_confirm") != "1":
                extra_context["extra_confirm_error"] = "Нужно дополнительное подтверждение для удаления кабинета."
                return render(request, self.delete_confirmation_template, extra_context, status=400)

            self.delete_model(request, room)
            messages.success(request, "Кабинет удалён (архивирован).")
            return redirect("admin:clinic_room_changelist")

        return render(request, self.delete_confirmation_template, extra_context)

    def delete_model(self, request, obj: Room):
        """
        Soft-delete room to preserve appointment history and avoid FK PROTECT issues.
        Also renames the room to free up the unique name.
        """
        ts = timezone.localtime(timezone.now()).strftime("%Y%m%d-%H%M%S")
        base = (obj.name or "Кабинет")[:80]
        new_name = f"{base} [удалён {ts}] #{obj.id}"
        obj.name = new_name[:128]
        obj.is_available = False
        obj.is_deleted = True
        obj.deleted_at = timezone.now()
        obj.save(update_fields=["name", "is_available", "is_deleted", "deleted_at"])
