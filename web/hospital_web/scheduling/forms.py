from __future__ import annotations

from django import forms

from clinic.models import Doctor, Patient, Room
from scheduling.models import Appointment
from scheduling.services.booking import create_appointment


class AppointmentCreateForm(forms.Form):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=True)
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), required=True)
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=True)
    appointment_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}), required=True)
    duration_minutes = forms.IntegerField(min_value=5, max_value=24 * 60, initial=60, required=True)
    room = forms.ModelChoiceField(queryset=Room.objects.filter(is_available=True, is_deleted=False), required=True)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, doctor: Doctor | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if doctor:
            self.fields["doctor"].initial = doctor
            self.fields["doctor"].widget = forms.HiddenInput()

        # Room options can be dynamically swapped by HTMX; keep base queryset narrow
        self.fields["room"].queryset = Room.objects.filter(is_available=True, is_deleted=False).order_by("name")

    def save(self) -> Appointment:
        cd = self.cleaned_data
        return create_appointment(
            doctor=cd["doctor"],
            patient=cd["patient"],
            room=cd["room"],
            appointment_date=cd["appointment_date"],
            appointment_time=cd["appointment_time"],
            duration_minutes=cd["duration_minutes"],
            notes=cd.get("notes", ""),
        )

