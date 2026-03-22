from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class PatientManager(models.Manager):
    """Return only patients that are not soft-deleted."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Patient(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patients",
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(
        "phone number",
        max_length=32,
        blank=True,
        default="",
        help_text="Optional if email is provided; at least one contact method is required.",
    )
    email = models.EmailField(
        "email address",
        blank=True,
        default="",
        help_text="Optional if phone is provided; at least one contact method is required.",
    )
    date_of_birth = models.DateField(null=True, blank=True)
    medical_history = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        db_index=True,
    )

    objects = PatientManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "patients"
        indexes = [
            models.Index(fields=["name"], name="patients_name_idx"),
            models.Index(fields=["phone"], name="patients_phone_idx"),
            models.Index(fields=["email"], name="patients_email_idx"),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def age_years(self) -> int | None:
        if not self.date_of_birth:
            return None
        today = timezone.localdate()
        born = self.date_of_birth
        years = today.year - born.year - (
            (today.month, today.day) < (born.month, born.day)
        )
        return years

    def clean(self) -> None:
        super().clean()
        phone = (self.phone or "").strip()
        email = (self.email or "").strip()
        if not phone and not email:
            raise ValidationError(
                {
                    "phone": "Enter a phone number or provide an email address.",
                    "email": "Enter an email address or provide a phone number.",
                }
            )

    def soft_delete(self) -> None:
        """Mark this patient and all active appointments as deleted (soft)."""
        from apps.appointments.models import Appointment

        now = timezone.now()
        Appointment.all_objects.filter(
            patient_id=self.pk,
            deleted_at__isnull=True,
        ).update(deleted_at=now, updated_at=now)
        self.deleted_at = now
        self.save(update_fields=["deleted_at", "updated_at"])

    def delete(self, using=None, keep_parents=False):
        self.soft_delete()
