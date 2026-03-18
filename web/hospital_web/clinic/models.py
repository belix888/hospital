from django.conf import settings
from django.db import models


class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name="Telegram ID")
    name = models.CharField(max_length=255, verbose_name="ФИО")
    specialization = models.CharField(max_length=255, verbose_name="Специализация")
    phone = models.CharField(max_length=64, blank=True, default="", verbose_name="Телефон")
    email = models.EmailField(blank=True, default="", verbose_name="Email")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"

    def __str__(self) -> str:
        return f"{self.name} ({self.specialization})"


class Patient(models.Model):
    name = models.CharField(max_length=255, verbose_name="ФИО")
    phone = models.CharField(max_length=64, verbose_name="Телефон")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"

    def __str__(self) -> str:
        return f"{self.name} ({self.phone})"


class Room(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name="Название")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    is_deleted = models.BooleanField(default=False, verbose_name="Удалён")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Удалён (дата)")

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"

    def __str__(self) -> str:
        return self.name
