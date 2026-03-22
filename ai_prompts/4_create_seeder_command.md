## Prompt_1

create a Django management command to seed the database with initial data.

Command name: seed_data

It should:

- Create a default provider user:
username: provider
email: [provider@test.com](mailto:provider@test.com)
password: p@ssW0rd
- Create 5 patients for this provider
- Create 10 appointments for this provider and patients

Use Django management commands.
File location should be:
apps/core/management/commands/seed_data.py

---

## Response

Here’s what was added.

### Layout

- `apps/core/management/__init__.py`
- `apps/core/management/commands/__init__.py`
- `apps/core/management/commands/seed_data.py`

### What it does

1. **Provider** — `get_or_create(username="provider")`, sets `email` to `provider@test.com`, `is_active=True`, and password `p@ssW0rd` (safe to run again: user is updated).
2. **Patients** — Deletes any existing seed patients for that provider (`patient1@seed.local` … `patient5@seed.local`), then creates **5** with phone, email, DOB, short history/allergies/notes.
3. **Appointments** — Deletes existing seed appointments (`notes="seed_data"`), then creates **10** with **distinct** `scheduled_at` values (2 hours apart from a base time tomorrow) so the `(provider, scheduled_at)` unique constraint is satisfied. Patients are assigned in rotation; statuses vary (scheduled, completed, cancelled, no_show).

### Run it

```bash
python manage.py seed_data
```

`apps.core` is already in `INSTALLED_APPS`, so Django discovers the command automatically. A test run completed successfully against your database.

***

## Prompt_2

- Use Faker library to generate fake patients data
- Use random future dates for appointments

***
## Response


Here’s what changed.

### `requirements.txt`
- Added **`Faker==40.11.0`** (installed in your venv).

### `apps/core/management/commands/seed_data.py`
- **Patients:** Built with **Faker** — `name`, `phone` (trimmed to 32 chars), `unique.email()`, `date_of_birth` (18–92), `text` for `medical_history`, `sentence` or **NKDA** for `allergies`. Each seeded patient has **`notes="seed_data"`** so reruns only remove prior seed rows (same marker as appointments).
- **Appointments:** **`scheduled_at`** values are **random between 1 and 120 days ahead**, timezone-aware (`get_current_timezone()`), seconds/microseconds zeroed so `(provider, scheduled_at)` stays unique. Up to 500 tries build **10 distinct** times; if that fails, it falls back to **2-hour slots** and logs a warning.
- **Appointments:** Random **`duration`** in `{15, 20, 30, 45, 60}`, random **`status`** from `AppointmentStatus`, **`reason`** from `fake.sentence()`.
- **`fake.seed_instance(random.randint(...))`** so each run differs; **`fake.unique.clear()`** after patients so email uniqueness doesn’t carry over oddly in the same process.

Run again with:

```bash
python manage.py seed_data
```
