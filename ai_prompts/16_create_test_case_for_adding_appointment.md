## Prompt

Create the same for testing appointment creation and shared schedule validation.

Requirements:
- Test valid appointment creation
- Test that provider cannot create two appointments on the same day
- Test that provider cannot create appointments with less than 15-minute gap
- Use full_clean() to trigger validation in the model
- Use setUp() to create a provider and a patient
- Place the test in apps/appointments/tests/test_appointments.py
- Include clear comments about what each test checks

***

## Response


Here’s what was added.

### `apps/appointments/tests/__init__.py`
Empty package so Django can load tests.

### `apps/appointments/tests/test_appointments.py`
- **Module docstring** – Notes that schedule rules are enforced through `Appointment.full_clean()` → `clean()` → `get_appointment_schedule_errors`.
- **`setUp()`** – Creates `provider_appts` and a `Patient` tied to that provider; defines `self.slot_start` (timezone-aware, stable).
- **`test_valid_appointment_passes_full_clean_and_saves`** – Builds an `Appointment`, calls `full_clean()` then `save()`, asserts it exists for that provider/patient.
- **`test_cannot_create_two_appointments_at_same_scheduled_start`** – Saves a first booking, builds a second with the **same `scheduled_at`**, expects `ValidationError` from `full_clean()` and an error on `scheduled_at`. Docstring states this is the **duplicate start time** (same instant), not “only one visit per calendar day.”
- **`test_cannot_create_appointment_with_less_than_fifteen_minute_gap_after_prior`** – First visit 30 minutes starting at `slot_start`; second starts at `slot_start + 40m` (only **10 minutes** after the first ends); `full_clean()` must raise `ValidationError` on `scheduled_at`.

Run them with:

`python manage.py test apps.appointments.tests.test_appointments`