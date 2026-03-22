from django import forms
from django.utils.translation import gettext_lazy as _
from unfold.widgets import BASE_INPUT_CLASSES

from .models import Patient

_INPUT = " ".join(BASE_INPUT_CLASSES)
_TEXTAREA = " ".join([*BASE_INPUT_CLASSES, "min-h-[120px]", "w-full"])


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = (
            "name",
            "phone",
            "email",
            "date_of_birth",
            "medical_history",
            "notes",
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": _INPUT, "autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"class": _INPUT, "autocomplete": "tel"}),
            "email": forms.EmailInput(attrs={"class": _INPUT, "autocomplete": "email"}),
            "date_of_birth": forms.DateInput(
                attrs={"class": _INPUT, "type": "date"},
            ),
            "medical_history": forms.Textarea(
                attrs={"class": _TEXTAREA, "rows": 4},
            ),
            "notes": forms.Textarea(
                attrs={"class": _TEXTAREA, "rows": 3},
            ),
        }
        labels = {
            "name": _("Full name"),
            "phone": _("Phone number"),
            "email": _("Email address"),
            "date_of_birth": _("Date of birth"),
            "medical_history": _("Medical history"),
            "notes": _("Notes"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
        self.fields["name"].required = True
