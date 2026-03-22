## Prompt

prevent to create more than one appointment in the same time and the gap time between the appointment and the next one shouldn't less than 15 mins

## Response


Here’s what was implemented.

### Rules (per provider, ignoring soft-deleted rows)

1. **No overlap** – If the new interval `[scheduled_at, scheduled_at + duration)` overlaps any existing one, saving is blocked (this also covers two visits starting at the same time; the DB unique on `(provider, scheduled_at)` still applies).
2. **15-minute buffer** – If the new visit is **after** another, the gap between **that visit’s end** and **this visit’s start** must be **≥ 15 minutes**. The same applies if the new visit is **before** another (gap between **this visit’s end** and **their start**).

### Code changes

- **`apps/appointments/models.py`** – `MIN_GAP_BETWEEN_APPOINTMENTS`, `get_appointment_schedule_errors()`, `Appointment.clean()`, and `Appointment.save()` calling `full_clean()` so admin and normal saves both validate. Soft-delete still uses `save(update_fields=["deleted_at", "updated_at"])` and **skips** `full_clean()` so it can’t fail on old data.
- **`apps/appointments/forms.py`** – `clean()` uses the same helper (clear errors on `scheduled_at`).
- **`apps/core/management/commands/seed_data.py`** – Seeds appointments in a single chain: each starts **duration + 15 minutes** after the previous one so `seed_data` still works.

Validation messages:

- Overlap: *“This time overlaps another appointment. Choose a different slot.”*
- Short gap: *“Allow at least 15 minutes between the end of one appointment and the start of the next.”*

If you want **only `scheduled`** visits to block the calendar (and `cancelled` / `completed` to free slots), that can be narrowed with a small filter on `status`.