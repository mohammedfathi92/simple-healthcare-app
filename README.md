# Healthcare System

A simple **healthcare provider portal** built with Django. Providers sign in, manage their patients, and schedule appointments from a dashboard-backed workflow. The app uses **Django Unfold** for a polished **Django admin** UI, **server-side DataTables** for list views, and **HTMX** for dynamic fragments in provider-facing screens (for example, patient search in the schedule-appointment modal without full page reloads).

**Highlights**

- Provider authentication (login / logout)
- Patient CRUD with soft delete and duplicate-phone safeguards
- Appointments with scheduling rules (no double booking at the same time, minimum 15-minute gap between visits)
- Provider dashboard with quick stats and today’s schedule
- Django admin for staff-facing management

---

## Project Structure

| Path | Purpose |
|------|---------|
| `config/` | Django project settings, root URL configuration |
| `apps/accounts/` | Custom user model, provider login |
| `apps/patients/` | Patient models, views, URLs |
| `apps/appointments/` | Appointment models, forms, validation, tests |
| `apps/core/` | Shared utilities (e.g. management commands, mixins) |
| `templates/` | HTML templates (portal layouts, Unfold overrides) |
| `static/` | CSS, JS, and vendor assets |
| `tests/` | Root-level tests (e.g. auth, patient creation) |
| `apps/appointments/tests/` | Appointment schedule validation tests |
| `ai_prompts/` | Task and AI prompt documentation used during development |
| `manage.py` | Django entry point |
| `.env.sample` | Example environment variables for local setup |

---

## Database Structure

The app targets **PostgreSQL**. Main logical tables:

### `users` (providers)

`CustomUser` extends Django’s user model (`db_table`: `users`).

| Column | Notes |
|--------|--------|
| `id` | Primary key |
| `username`, `password` | Login credentials |
| `email`, `first_name`, `last_name` | Standard user fields |
| `is_staff`, `is_active`, `is_superuser` | Permissions |
| `date_joined`, `last_login` | Timestamps |
| `created_at`, `updated_at` | App-specific audit fields |

### `patients`

| Column | Notes |
|--------|--------|
| `id` | Primary key |
| `provider_id` | FK → `users` (owner) |
| `name` | Full name |
| `phone`, `email` | Contact (at least one required) |
| `date_of_birth` | Optional |
| `medical_history`, `allergies`, `notes` | Text |
| `created_at`, `updated_at` | Audit |
| `deleted_at` | Soft delete (null = active) |

### `appointments`

| Column | Notes |
|--------|--------|
| `id` | Primary key |
| `provider_id` | FK → `users` |
| `patient_id` | FK → `patients` |
| `scheduled_at` | Start (timezone-aware) |
| `duration` | Length in minutes |
| `status` | e.g. scheduled, completed, cancelled |
| `reason`, `diagnosis`, `prescription`, `notes` | Text |
| `created_at`, `updated_at` | Audit |
| `deleted_at` | Soft delete |

Unique active slot per provider: `(provider_id, scheduled_at)` when `deleted_at` is null. Model validation enforces non-overlapping intervals and a **15-minute** minimum gap between consecutive bookings.

---

## AI Prompts Folder

All AI-assisted task descriptions and requirements used while building this project live under **`/ai_prompts`**. Each file is a numbered Markdown prompt (features, tests, UI, validation, etc.). **Keeping prompts in this folder is part of the documented workflow** for traceability and reproducibility.

---

## Requirements

| Tool | Version (recommended) |
|------|------------------------|
| **Python** | 3.12+ (required for Django 6.x) |
| **pip** | 24+ (recent pip is fine) |
| **PostgreSQL** | 14+ (12+ generally works with `psycopg2`) |

Install Python dependencies in a virtual environment (see below). Typical packages include **Django**, **django-environ**, **django-unfold**, **django-htmx**, **django-crispy-forms**, **psycopg2-binary**, and **Faker** (for the optional seed command).

---

## Installation

1. **Clone** the repository and enter the project directory.

2. **Create and activate a virtual environment** (example):

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies** (adjust if you maintain a `requirements.txt`):

   ```bash
   pip install Django django-environ django-unfold django-htmx django-crispy-forms psycopg2-binary Faker
   ```

4. **Configure environment variables**: copy the sample file and edit values.

   ```bash
   copy .env.sample .env
   ```

   On macOS/Linux use `cp .env.sample .env`.

   Set at least `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and the `DATABASE_*` variables to match your PostgreSQL instance (see `.env.sample`).

5. **Apply migrations**:

   ```bash
   python manage.py migrate
   ```

6. **(Optional)** Create a superuser and load demo data:

   ```bash
   python manage.py createsuperuser
   python manage.py seed_data
   ```

7. **(Optional)** Login:

   ```bash
   username: provider
   password: p@ssW0rd
   ```

---

## Running the Server

```bash
python manage.py runserver
```

Then open the URL shown in the terminal (usually `http://127.0.0.1:8000/`). Use `/login/` for the provider portal and `/admin/` for Django admin (Unfold).

---

## Tests

Automated tests cover:

- **Provider login** — successful login and rejection on bad password (`tests/accounts/test_auth.py`)
- **Patient creation** — logged-in provider can create a patient linked to their account (`tests/patients/test_patients.py`)
- **Appointments** — valid booking, duplicate start time, and violations of the **15-minute gap** rule via `full_clean()` (`apps/appointments/tests/test_appointments.py`)

Run the full suite:

```bash
python manage.py test
```

Run a subset by label, for example:

```bash
python manage.py test tests.accounts.test_auth
python manage.py test tests.patients.test_patients
python manage.py test apps.appointments.tests.test_appointments
```

---

## Conclusion / Notes

This project is structured to show **clear separation of apps**, **consistent validation** at the model layer, **test-backed behavior** for auth and scheduling rules, and a **documented workflow** (including the `ai_prompts` folder) suitable for a professional, maintainable Django codebase.
