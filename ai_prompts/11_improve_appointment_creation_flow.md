## prompt

improve the appointment creation flow.

When the user clicks "Schedule Appointment", open a Bootstrap modal (popup) that asks for:
- Patient name
- Phone
- Email

While the user is typing, search for existing patients using HTMX (live search).

If similar patients are found, show a list inside the modal with:
- Name
- Phone
- Email
- A button: "This is the patient"

If the user selects a patient, redirect to the appointment creation page with the patient already selected.

If no patient is found, show a button:
"Create New Patient"

When clicked, redirect to the patient creation page and pre-fill:
- Name
- Phone
- Email

On the patient form page, add two buttons:
- Save Patient
- Save Patient & Create Appointment

If "Save Patient & Create Appointment" is clicked, save the patient and redirect to the appointment creation page with this patient selected.

Technical notes:

- Use HTMX for live patient search (no page reload)
- Use Bootstrap modal for the popup
- Use query parameters to pass name, phone, email between pages
- Use class-based views
- Keep the code clean and simple

***

## Response


Here’s what was implemented:

### 1. **`PatientScheduleSearchFragmentView`** (`apps/patients/views.py`)
- `GET /patients/api/schedule-search/?name=&phone=&email=`
- OR-filters on your patients: each non-empty term matches **name**, **phone**, or **email** (`icontains`), up to 20 rows.
- Returns HTML only (for HTMX).

### 2. **URL** (`apps/patients/urls.py`)
- Registered **before** `patients/<int:pk>/`.

### 3. **Partial** `templates/patients/partials/schedule_search_results.html`
- No input: short hint.
- Matches: list with name / phone / email and **“This is the patient”** → `{% url 'appointments:create' %}?patient={{ p.pk }}`.
- Matches + footer: **“Create new patient”** (same behavior as below).
- No matches: **“Create new patient”** only.

### 4. **Modal** `templates/appointments/includes/schedule_modal.html`
- Bootstrap **5.3** modal `#scheduleAppointmentModal`.
- Form fields: name, phone, email.
- Inner `div` uses **HTMX**: `hx-get` → `schedule_search`, `hx-trigger="input delay:400ms"`, `hx-include` whole form, `hx-target` results, `hx-indicator` for “Searching…”.
- Script (after Bootstrap in page order): builds `patients:create?name=&phone=&email=` for **Create new patient**; clears results when the modal opens; delegates clicks for dynamically inserted buttons.

### 5. **Base layout** (`templates/base.html`)
- `extra_portal_head` (Bootstrap CSS, etc.).
- **`portal_bootstrap_scripts` before `schedule_modal`** so Bootstrap loads before the modal script.
- `schedule_modal` block for the include.

### 6. **Dashboard & appointments list**
- **Schedule appointment** opens the modal (no direct link to create).
- Same blocks: Bootstrap CSS/JS + `{% include "appointments/includes/schedule_modal.html" %}`.

### 7. **`AppointmentCreateView`**
- `get_initial()`: `?patient=<pk>` pre-selects patient when the pk belongs to the current provider.

### 8. **`PatientCreateView`**
- `get_initial()` from `?name=`, `?phone=`, `?email=`.
- `get_success_url()`: if `save_and_schedule` in POST → redirect to `appointments:create?patient=<new_pk>`.
- Duplicate-phone flow keeps intent via **`save_and_schedule_intent`** + hidden `save_and_schedule` on the confirm form.

### 9. **Patient form** (`templates/patients/patient_form.html`)
- **Save patient** (existing primary submit).
- **Save patient & create appointment** (`name="save_and_schedule" value="1"`) when `show_save_and_schedule` is true (create only).
- **PatientUpdateView** sets `show_save_and_schedule` to **False**.

### 10. **CSS** (`static/css/custom.css`)
- `#schedule-search-indicator` visibility tied to **`.htmx-request`**.

---

**Note:** Bootstrap is loaded only on **dashboard** and **appointments list** (plus your global `custom.css` after it). Header layout still avoids Bootstrap’s `.container`, so width should stay stable.

If HTMX doesn’t fire on **input** in your browser, change the trigger to  
`hx-trigger="keyup changed delay:400ms"` on that `div`.