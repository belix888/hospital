from __future__ import annotations

from django.conf import settings
from django.db import models


class ReportStatus(models.TextChoices):
    PENDING = "pending", "В очереди"
    DONE = "done", "Готово"
    FAILED = "failed", "Ошибка"


class ReportKind(models.TextChoices):
    DOCTOR_MONTH = "doctor_month", "Записи врача за месяц"
    ALL_DOCTORS_MONTH = "all_doctors_month", "Записи всех врачей за месяц"


class ReportJob(models.Model):
    kind = models.CharField(max_length=64, choices=ReportKind.choices, verbose_name="Тип отчёта")
    status = models.CharField(max_length=32, choices=ReportStatus.choices, default=ReportStatus.PENDING, verbose_name="Статус")
    params = models.JSONField(default=dict, verbose_name="Параметры")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Запрошено пользователем",
    )
    file = models.FileField(upload_to="reports/", null=True, blank=True, verbose_name="Файл")
    error = models.TextField(blank=True, default="", verbose_name="Ошибка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Завершено")

    class Meta:
        verbose_name = "Задание отчёта"
        verbose_name_plural = "Задания отчётов"

    def __str__(self) -> str:
        return f"{self.kind} #{self.id} ({self.status})"
