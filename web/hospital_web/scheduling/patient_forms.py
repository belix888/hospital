from __future__ import annotations

from django import forms

from clinic.models import Patient


class PatientQuickAddForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["name", "phone", "birth_date"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

