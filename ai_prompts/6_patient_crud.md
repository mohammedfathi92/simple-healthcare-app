## Prompt_1

Patient:
create full crud for Patient with the following:

- list of patiens of the provider that show the following data (Name, phone, email, current age (based on the birth of date), upcoming appointment, created at, action buttons)
- acction buttons in the list have (edit, remove with confirmation alert)
- create/edit page with the (name, phone, email, date of birth, medical history, notes)
- check first if the phone exists or not if yes give the user options of using the existed record without adding new one or add new one with the same phone number

***
## Response


Here’s what was implemented.

### URLs (`apps/patients/urls.py`, wired in `config/urls.py`)
| Path | Name |
|------|------|
| `/patients/` | `patients:list` |
| `/patients/add/` | `patients:create` |
| `/patients/<id>/edit/` | `patients:update` |
| `/patients/<id>/delete/` | `patients:delete` |

### Model (`apps/patients/models.py`)
- **`age_years`** — computed from `date_of_birth` (or `None` if missing).

### Form (`apps/patients/forms.py`)
- **`PatientForm`** — `name`, `phone`, `email`, `date_of_birth`, `medical_history`, `notes` (Unfold-style widgets).  
- **`name`** required; phone/email follow model `clean()` (at least one). **`allergies`** unchanged (admin only).

### Views (`apps/patients/views.py`)
- **`PatientListView`** — only `request.user`’s patients; annotates **`next_appointment_at`** (earliest `scheduled_at >= now`); columns supported in the template; pagination 25.
- **`PatientCreateView`** / **`PatientUpdateView`** — after a valid POST, if **phone** (stripped) matches another patient for the same provider (on update, excluding current pk) and **`confirm_duplicate`** is not in POST, the form is shown again with **`show_duplicate_warning`** and links to **edit** existing rows plus a second form (hidden fields + `confirm_duplicate=1`) to **create/update anyway** with the same phone.
- **`PatientDeleteView`** — scoped queryset; success message after delete.

### Templates (`templates/patients/`)
- **`patient_list.html`** — table: name, phone, email, age, upcoming appt (local date/time), created, **Edit** + **Remove** (link to confirm page).
- **`patient_form.html`** — create/edit + duplicate-phone panel.
- **`patient_confirm_delete.html`** — confirm + `confirm()` on submit.

### Navigation
- Header **Patients** link in `templates/base.html`.
- Dashboard **Add patient** now points to **`patients:create`**.

**Note:** “Upcoming” in the list is the **next** appointment from **now** (`scheduled_at >= now`). **Remove** goes to the confirm page; the list no longer uses an inline delete POST (avoids invalid nested forms and matches a clear confirm step).