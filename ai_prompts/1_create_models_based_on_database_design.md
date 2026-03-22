## Prompt_1
Create Django models for this database design:

users (providers)
- id, username, email, password, first_name, last_name, is_active, created_at, updated_at

patients
- id, provider (FK to users), name, phone, email, date_of_birth, medical_history, allergies, notes, created_at, updated_at
- unique (provider, phone)
- indexes on name, phone, email


appointments
- id, provider (FK to users), patient (FK to patients), scheduled_at, duration (minutes), status (scheduled, completed, cancelled, no_show), reason, diagnosis, prescription, notes, created_at, updated_at
- unique(provider, scheduled_at)
- indexes on provider+scheduled_at and patient

***

## Response


Here’s what was added and how it maps to your design.

### Summary

- **`apps.accounts.CustomUser`** — Subclasses `AbstractUser` (so you still get `username`, `email`, `password`, `first_name`, `last_name`, `is_active`, plus Django’s auth fields). Adds `created_at` / `updated_at`. Physical table name: **`users`** via `Meta.db_table`.
- **`apps.patients.Patient`** — `provider` → `CustomUser`, all listed fields, **`UniqueConstraint` on `(provider, phone)`**, indexes on **`name`**, **`phone`**, **`email`**.
- **`apps.appointments.Appointment`** — `provider` and `patient` FKs, `duration` as minutes (`PositiveIntegerField`), `status` via `AppointmentStatus` `TextChoices`, **`UniqueConstraint` on `(provider, scheduled_at)`**, composite index on **`(provider, scheduled_at)`**, index on **`patient`**.

`config/settings.py` now includes `apps.accounts`, `apps.patients`, `apps.appointments` and **`AUTH_USER_MODEL = "accounts.CustomUser"`**. Initial migrations were created and **`migrate`** completed successfully.

### Implementation references

```1:15:c:\laragon\www\Backswing\healthcare-system\apps\accounts\models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    """Healthcare provider user."""

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
```

```6:39:c:\laragon\www\Backswing\healthcare-system\apps\patients\models.py
class Patient(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patients",
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True)
    # ...
    class Meta:
        db_table = "patients"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "phone"],
                name="patients_provider_phone_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["name"], name="patients_name_idx"),
            models.Index(fields=["phone"], name="patients_phone_idx"),
            models.Index(fields=["email"], name="patients_email_idx"),
        ]
```

```17:54:c:\laragon\www\Backswing\healthcare-system\apps\appointments\models.py
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
    # ...
    class Meta:
        db_table = "appointments"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "scheduled_at"],
                name="appointments_provider_scheduled_at_uniq",
            ),
        ]
        indexes = [
            models.Index(
                fields=["provider", "scheduled_at"],
                name="appts_provider_scheduled_idx",
            ),
            models.Index(fields=["patient"], name="appts_patient_idx"),
        ]
```

### Note on `unique(provider, phone)`

`phone` is optional (`blank=True`). Stored values use the empty string when blank, so **at most one patient per provider can have a blank phone** under this unique constraint. If you need several patients with “no phone,” we can switch to `null=True` and/or a partial unique constraint (database-dependent).

Admin registrations for all three models are in each app’s `admin.py`.


***
***

## Prompt_2

Edit Patient where either the phone number or the email must be provided. 
Both fields should be optional individually but the model should validate that at least one of them is filled. 
Include the clean() method for validation and proper field definitions.

and remove the UniqueConstraint for phone, do that in the same initial migration file no need to create new one

***

## Response 


Here’s what changed.

### `Patient` model (`apps/patients/models.py`)

- **`phone`** and **`email`** stay optional in the schema (`blank=True`) with **`default=""`** so values are consistently strings and `clean()` can treat “empty” as missing after `.strip()`.
- **`verbose_name`** and **`help_text`** spell out that at least one contact method is required.
- **`clean()`** calls `super().clean()`, then requires **either** a non-empty stripped `phone` **or** a non-empty stripped `email**; otherwise it raises **`ValidationError`** on both fields so errors show next to each input in forms/admin.

### Migration (`apps/patients/migrations/0001_initial.py`)

- Removed the **`UniqueConstraint`** on `(provider, phone)` from `CreateModel` options.
- Aligned **`phone`** / **`email`** definitions with the model (`default=""`, `verbose_name`, `help_text`).

`makemigrations --dry-run` reports **no changes** (model and `0001_initial` stay in sync).

**Existing database:** If you already ran the old `0001_initial` (with the unique constraint), SQLite/Postgres will still have that constraint until you drop it or rebuild the DB. Editing `0001_initial` only affects **new** `migrate` runs from scratch; for an existing DB you’d need a follow-up migration or a manual drop— you asked not to add a new migration file, so that’s the tradeoff.

