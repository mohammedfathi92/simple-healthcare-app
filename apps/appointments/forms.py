from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from unfold.widgets import BASE_INPUT_CLASSES

from apps.patients.models import Patient

from .models import Appointment, get_appointment_schedule_errors

_INPUT = " ".join(BASE_INPUT_CLASSES)
_TEXTAREA = " ".join([*BASE_INPUT_CLASSES, "min-h-[100px]", "w-full"])


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = (
            "patient",
            "scheduled_at",
            "duration",
            "status",
            "reason",
            "diagnosis",
            "prescription",
            "notes",
        )
        widgets = {
            "patient": forms.Select(attrs={"class": _INPUT}),
            "scheduled_at": forms.DateTimeInput(
                attrs={"class": _INPUT, "type": "datetime-local", "step": "60"},
                format="%Y-%m-%dT%H:%M",
            ),
            "duration": forms.NumberInput(
                attrs={"class": _INPUT, "min": 1, "step": 1},
            ),
            "status": forms.Select(attrs={"class": _INPUT}),
            "reason": forms.Textarea(attrs={"class": _TEXTAREA, "rows": 3}),
            "diagnosis": forms.Textarea(attrs={"class": _TEXTAREA, "rows": 3}),
            "prescription": forms.Textarea(attrs={"class": _TEXTAREA, "rows": 3}),
            "notes": forms.Textarea(attrs={"class": _TEXTAREA, "rows": 3}),
        }
        labels = {
            "patient": _("Patient"),
            "scheduled_at": _("Scheduled date & time"),
            "duration": _("Duration (minutes)"),
            "status": _("Status"),
            "reason": _("Reason / purpose"),
            "diagnosis": _("Diagnosis"),
            "prescription": _("Prescription"),
            "notes": _("Notes"),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["patient"].queryset = Patient.objects.filter(provider=user).order_by(
                "name"
            )
        self.fields["duration"].min_value = 1
        self.fields["scheduled_at"].input_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]

    def clean_patient(self):
        patient = self.cleaned_data.get("patient")
        if patient is None or self.user is None:
            return patient
        if patient.provider_id != self.user.pk:
            raise ValidationError(_("Select a patient from your list."))
        return patient

    def clean(self):
        cleaned = super().clean()
        if self.user is None:
            return cleaned
        scheduled_at = cleaned.get("scheduled_at")
        duration = cleaned.get("duration")
        patient = cleaned.get("patient")
        if scheduled_at is None or patient is None or duration is None:
            return cleaned
        errs = get_appointment_schedule_errors(
            self.user,
            patient,
            scheduled_at,
            int(duration),
            exclude_pk=self.instance.pk if self.instance.pk else None,
        )
        if errs:
            raise ValidationError(errs)
        return cleaned
