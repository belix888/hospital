from django.db import models

from clinic.models import Doctor, Patient, Room


class AppointmentStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Запланировано"
    COMPLETED = "completed", "Завершено"
    CANCELLED = "cancelled", "Отменено"


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="appointments", verbose_name="Врач")
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="appointments", verbose_name="Пациент")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="appointments", verbose_name="Кабинет")

    appointment_date = models.DateField(verbose_name="Дата")
    appointment_time = models.TimeField(verbose_name="Время")
    duration_minutes = models.PositiveIntegerField(default=60, verbose_name="Длительность (мин)")
    status = models.CharField(
        max_length=32,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
        verbose_name="Статус",
    )
    notes = models.TextField(blank=True, default="", verbose_name="Заметки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    extension_prompt_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Напоминание о продлении отправлено")
    completion_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Уведомление о завершении отправлено")

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        indexes = [
            models.Index(fields=["appointment_date", "room"]),
            models.Index(fields=["doctor", "appointment_date"]),
        ]
        ordering = ["appointment_date", "appointment_time", "room_id"]

    def __str__(self) -> str:
        return f"{self.appointment_date} {self.appointment_time} {self.room} {self.doctor}"
