## Prompt

This is a simple healthcare app
here is the project structure I want:

Root/  
├── config/  
│   ├── settings.py  
│   ├── urls.py  
│   └── asgi.py  
├── apps/  
│   ├── accounts/  
│   ├── patients/  
│   ├── appointments/  
│   └── core/  
├── templates/  
├── static/  
├── requirements.txt  
├── .env  
├── [manage.py](http://manage.py)  
└── README.md

Database Design

1. users (CustomUser / providers)

- id, username, email, password, first_name, last_name, is_active, created_at, updated_at

1. patients

- id, provider_id, name, phone, email, date_of_birth, medical_history, allergies, notes, created_at, updated_at

1. appointments

- id, provider_id, patient_id, scheduled_at, duration, status (scheduled, completed, cancelled, no_show), reason, diagnosis, prescription, notes, created_at, updated_at
- unique(provider_id, scheduled_at)
- indexes: provider_id + scheduled_at, patient_id

give a clear plan for the models first 

---

## Response

Here is a concise **models plan** that matches your layout and schema, without implementing code yet.

---

## Where each model lives


| Model         | App                 | Rationale                                                              |
| ------------- | ------------------- | ---------------------------------------------------------------------- |
| `CustomUser`  | `apps.accounts`     | Auth and “provider” identity in one place; set `AUTH_USER_MODEL` here. |
| `Patient`     | `apps.patients`     | Patient records scoped to a provider.                                  |
| `Appointment` | `apps.appointments` | Scheduling and visit metadata; depends on user + patient.              |


`apps.core` can hold shared utilities (base `TimeStampedModel` mixin, enums) if you want to avoid repeating `created_at` / `updated_at`.

---

## 1. `CustomUser` (providers)

**Base:** subclass `AbstractUser` (keeps Django auth: password hashing, permissions, `is_staff`, etc.).

**Already on `AbstractUser` (do not duplicate as custom columns):**  
`id`, `username`, `email`, `password`, `first_name`, `last_name`, `is_active` (plus `is_staff`, `is_superuser`, `date_joined`, `last_login` unless you explicitly strip them later).

**Add explicitly to match your list:**

- `created_at` — set on create (e.g. default `timezone.now` or mirror first save).
- `updated_at` — auto-update on each save.

**Decisions to lock in before coding:**

- **Email:** If providers log in with email, add `USERNAME_FIELD = "email"` and enforce `unique=True` on `email` (and often blank `username` or keep username for admin). Your spec lists both username and email; that is fine as long as login rules are clear.
- **“Provider only”:** If every user in this table is a provider, you can skip a `role` field for now; add it later if you introduce patients-as-users or staff.

---

## 2. `Patient`

**Purpose:** A patient record owned by exactly one provider.


| Concept                                 | Django shape                                                      |
| --------------------------------------- | ----------------------------------------------------------------- |
| `provider_id`                           | `ForeignKey` to `CustomUser`, e.g. `related_name="patients"`.     |
| `name`                                  | `CharField` (or split into first/last later if you want).         |
| `phone`                                 | `CharField` (store as string; optional `E.164` validation later). |
| `email`                                 | `EmailField`, `blank=True` if not always known.                   |
| `date_of_birth`                         | `DateField`, `null=True` if unknown.                              |
| `medical_history`, `allergies`, `notes` | `TextField`, all optional as needed.                              |
| `created_at`, `updated_at`              | Same pattern as user (or inherit from a core mixin).              |


**Delete behavior:** Prefer `on_delete=models.PROTECT` on provider if you must not lose clinical rows when a user is removed; use `CASCADE` only if deleting a provider should wipe their patients by design.

---

## 3. `Appointment`

**Purpose:** One scheduled (or completed) encounter between a provider and a patient.


| Concept                                        | Django shape                                                                                               |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `provider_id`                                  | `ForeignKey(CustomUser)`, e.g. `related_name="appointments"`.                                              |
| `patient_id`                                   | `ForeignKey(Patient)`, scoped to the same provider in app logic; DB can enforce with checks or validation. |
| `scheduled_at`                                 | `DateTimeField` (timezone-aware with `USE_TZ=True`).                                                       |
| `duration`                                     | `PositiveIntegerField` (minutes) **or** `DurationField` — pick one convention and stick to it.             |
| `status`                                       | `CharField` with `TextChoices`: `scheduled`, `completed`, `cancelled`, `no_show`.                          |
| `reason`, `diagnosis`, `prescription`, `notes` | `TextField` (nullable/blank as appropriate).                                                               |
| `created_at`, `updated_at`                     | Same as above.                                                                                             |


**Constraints (your spec):**

- **Unique `(provider, scheduled_at)`:** `Meta.constraints = [models.UniqueConstraint(fields=["provider", "scheduled_at"], name="…")]`.  
**Note:** This forbids two appointments for the same provider at the *exact same* timestamp. If you ever need concurrent slots (e.g. different rooms), you would relax this (e.g. include `room` or use a finer-grained key).

**Indexes (your spec):**

- Composite index on `(provider_id, scheduled_at)` — aligns with calendar queries; Django often creates an index for the unique constraint on those columns; verify after migration and add `indexes` only if something is missing.
- Index on `patient_id` — `Meta.indexes = [models.Index(fields=["patient"]), …]`.

**Integrity:** In forms/services, ensure `appointment.patient.provider_id == appointment.provider_id` so a provider cannot attach another provider’s patient.

**Delete behavior:** Same idea as patients — `PROTECT` vs `CASCADE` on provider/patient according to retention policy.

---

## 4. Implementation order (migrations)

1. `CustomUser` + `AUTH_USER_MODEL` in settings (before any FK to user).
2. `Patient` (FK to user).
3. `Appointment` (FKs to user and patient + constraints/indexes).

---

## 5. Optional small refinements (not required for v1)

- Shared `TimeStampedModel` in `core` with `created_at` / `updated_at` and `abstract = True`.  
- `__str_`_ methods and `ordering` on `Appointment` (e.g. by `-scheduled_at`).  
- Database-level check that appointment’s patient belongs to the same provider (PostgreSQL check constraint via `RunSQL`, or strict validation in the service layer only).

---

If you want the next step to be **actual `models.py` code** and `settings` wired to this layout, say so and we can align it with your target `config/settings/` split and `apps.`* package paths.