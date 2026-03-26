from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

MIN_GAP_BETWEEN_APPOINTMENTS = timedelta(minutes=15)


def get_appointment_schedule_errors(
    provider,
    patient,
    scheduled_at,
    duration_minutes: int,
    *,
    exclude_pk=None,
) -> dict:
    """
    Return field errors if this slot overlaps another appointment or is within
    MIN_GAP_BETWEEN_APPOINTMENTS of another (same provider or patient, non-deleted).
    """
    if scheduled_at is None or duration_minutes is None:
        return {}
    duration_td = timedelta(minutes=int(duration_minutes))
    end = scheduled_at + duration_td
    window_start = scheduled_at - duration_td - MIN_GAP_BETWEEN_APPOINTMENTS
    window_end = end + MIN_GAP_BETWEEN_APPOINTMENTS
    base_qs = Appointment.objects.filter(
        Q(provider=provider) | Q(patient=patient)
    )
    qs = base_qs.filter(
        scheduled_at__gte=window_start,
        scheduled_at__lt=window_end,
    )
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
        base_qs = base_qs.exclude(pk=exclude_pk)


    prev_provider = (
        base_qs.filter(provider=provider, scheduled_at__lt=scheduled_at)
        .order_by("-scheduled_at")
        .first()
    )
    prev_patient = (
        base_qs.filter(patient=patient, scheduled_at__lt=scheduled_at)
        .order_by("-scheduled_at")
        .first()
    )
    candidates = list(qs)
    if prev_provider is not None:
        candidates.append(prev_provider)
    if prev_patient is not None:
        candidates.append(prev_patient)

    seen = set()
    for other in candidates:
        if other.pk in seen:
            continue
        seen.add(other.pk)
        o_start = other.scheduled_at
        o_end = o_start + timedelta(minutes=int(other.duration))
        if scheduled_at < o_end and end > o_start:
            return {
                "scheduled_at": _(
                    "This time overlaps another appointment. Choose a different slot."
                ),
            }
        if end <= o_start:
            if o_start - end < MIN_GAP_BETWEEN_APPOINTMENTS:
                return {
                    "scheduled_at": _(
                        "Allow at least 15 minutes between the end of one appointment "
                        "and the start of the next."
                    ),
                }
        elif scheduled_at >= o_end:
            if scheduled_at - o_end < MIN_GAP_BETWEEN_APPOINTMENTS:
                return {
                    "scheduled_at": _(
                        "Allow at least 15 minutes between the end of one appointment "
                        "and the start of the next."
                    ),
                }
    return {}


class AppointmentStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    NO_SHOW = "no_show", "No show"


class AppointmentManager(models.Manager):
    """Return only appointments that are not soft-deleted."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Appointment(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    scheduled_at = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes.")
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
    )
    reason = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        db_index=True,
    )

    objects = AppointmentManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "appointments"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "scheduled_at"],
                condition=Q(deleted_at__isnull=True),
                name="appointments_provider_scheduled_active_uniq",
            ),
        ]
        indexes = [
            models.Index(
                fields=["provider", "scheduled_at"],
                name="appts_provider_scheduled_idx",
            ),
            models.Index(fields=["patient", "scheduled_at"], name="appts_patient_sched_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.patient} @ {self.scheduled_at}"

    def clean(self):
        super().clean()
        if (
            self.provider_id
            and self.patient_id
            and self.scheduled_at is not None
            and self.duration is not None
        ):
            errs = get_appointment_schedule_errors(
                self.provider,
                self.patient,
                self.scheduled_at,
                self.duration,
                exclude_pk=self.pk,
            )
            if errs:
                raise ValidationError(errs)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        if update_fields is not None and set(update_fields) <= {
            "deleted_at",
            "updated_at",
        }:
            super().save(*args, **kwargs)
            return
        self.full_clean()
        super().save(*args, **kwargs)

    def soft_delete(self) -> None:
        now = timezone.now()
        self.deleted_at = now
        self.save(update_fields=["deleted_at", "updated_at"])

    def delete(self, using=None, keep_parents=False):
        self.soft_delete()
