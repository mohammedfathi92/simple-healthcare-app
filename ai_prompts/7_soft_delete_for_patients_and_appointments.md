## Prompt
use soft delete for patient and their appointments

***

## Response


Here’s what was implemented.

### `Patient` (`apps/patients/models.py`)
- **`deleted_at`** — nullable `DateTimeField`, indexed.
- **`PatientManager`** — default **`objects`** only returns rows with **`deleted_at IS NULL`**.
- **`all_objects`** — full queryset (admin/shell only if you switch to it).
- **`soft_delete()`** — sets **`deleted_at`** on the patient and **`update`s** all of their appointments that are still active (`deleted_at` null) to the same timestamp (updates **`updated_at`** too).
- **`delete()`** — calls **`soft_delete()`** (no hard delete through the model API).

### `Appointment` (`apps/appointments/models.py`)
- **`deleted_at`** — same pattern.
- **`AppointmentManager`** / **`all_objects`** — same idea as patients.
- **`delete()`** — soft-deletes that row only.
- **Unique constraint** — replaced with a **partial** unique on **`(provider, scheduled_at)`** where **`deleted_at IS NULL`** (`appointments_provider_scheduled_active_uniq`), so a slot can be reused after an appointment is soft-deleted.

### Migrations
- **`patients.0002_soft_delete`** — adds **`deleted_at`**.
- **`appointments.0002_soft_delete`** — drops the old unique constraint, adds **`deleted_at`**, adds the conditional unique constraint.

### Admin
- **`delete_queryset`** on **`PatientAdmin`** and **`AppointmentAdmin`** loops and calls **`obj.delete()`** so bulk “delete selected” is soft delete, not a raw SQL **`DELETE`**.

### UI / copy
- Provider delete confirmation + success message describe **hiding** the patient and their appointments, not wiping the DB.

### Already correct
- **`Patient.objects`** / **`Appointment.objects`** in dashboard, patient CRUD, list subquery, and duplicate-phone checks only see **active** rows.

Apply migrations if you haven’t: **`python manage.py migrate`**.
