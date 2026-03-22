## Prompt

let's do the same style for appointments crud 

- same patients crud style
- content of the list page > patient name, patient phone, patient email, schedualed at, created_at
--- filter the list by all the showed columns and for scheduale at column make the filteration as a date input with rang

- make create/edit and remove action buttons and pages

***

## Response


Here’s what was added for **portal appointments CRUD**, aligned with patients (Unfold + `list-dt-card` / DataTables).

### Routes (`apps/appointments/urls.py`, included in `config/urls.py`)
- `GET /appointments/api/datatable/` — server-side DataTables JSON  
- `GET /appointments/` — list  
- `GET/POST /appointments/add/` — create  
- `GET/POST /appointments/<id>/edit/` — update  
- `GET/POST /appointments/<id>/delete/` — soft delete (same as model `delete()`)

### List (`templates/appointments/appointment_list.html`)
- Columns: **patient name**, **phone**, **email**, **scheduled at**, **created**, **actions** (Edit / Remove).  
- **Filters** (above the table, styled with new `.list-dt-filters-*` in `custom.css`):  
  - Text (debounced ~400ms): name, phone, email  
  - **Date range**: scheduled **from/to** (full local days)  
  - **Date range**: created **from/to** (by `created_at` **date**)  
- DataTables: `searching: false`, `dom: "lrtip"` so only these filters apply (no extra global box).

### Backend (`apps/appointments/views.py`)
- `AppointmentDataTableAjaxView` reads `filter_patient_name`, `filter_patient_phone`, `filter_patient_email`, `filter_scheduled_from`, `filter_scheduled_to`, `filter_created_from`, `filter_created_to` (with normal `draw` / `start` / `length` / `order`).  
- Queryset scoped to `provider=request.user`, `select_related("patient")`.

### Forms (`apps/appointments/forms.py`)
- Fields: patient, scheduled_at (`datetime-local`), duration, status, reason, diagnosis, prescription, notes.  
- Patients limited to the current provider; **duplicate slot** check for another **active** appointment at the same `scheduled_at` (same rule as the DB constraint).

### Templates
- `appointment_form.html` — same pattern as patient form (back link, Unfold fields/buttons).  
- `appointment_confirm_delete.html` — same pattern as patient delete.

### Navigation
- **`base.html`**: **Appointments** link next to Patients.  
- **`dashboard.html`**: **Schedule Appointment** → `appointments:create` (no longer admin add).

### CSS (`static/css/custom.css`)
- **`.list-dt-filters-grid`**, **`.list-dt-filter-field`**, **`.list-dt-filter-input`** — same tokens as the existing list DataTable controls.

Open **`/appointments/`** to use the list; create/edit/delete match the patients portal flow.