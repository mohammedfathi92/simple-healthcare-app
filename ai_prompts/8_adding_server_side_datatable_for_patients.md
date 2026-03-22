## Prompt

- Use datatable with advanced server paginations for showing the patients list

- Adding search by name, phone, email

- Keep the unfold dashboard style with bootstrap 5

***
## Response

Here’s what was added.

### Server-side DataTables API
- **URL:** `/patients/api/datatable/` (`patients:datatable`)
- **View:** `PatientDataTableAjaxView` — `GET`, login required, scoped to `request.user` as provider
- **DataTables protocol:** `draw`, `recordsTotal`, `recordsFiltered`, `data[]`
- **Pagination:** `start` + `length` (page size capped at **100**)
- **Search:** single box, applied with **OR** on **`name`**, **`phone`**, **`email`** (`icontains`)
- **Ordering:** columns map to `name`, `phone`, `email`, `date_of_birth`, `next_appointment_at`, `created_at`; **Age** uses DOB so **asc = youngest first**; actions column not sortable
- **Rows:** include `edit_url` / `delete_url` for Bootstrap action buttons

### List page
- **`PatientListView`** is now a **`TemplateView`** (no server-rendered table rows).
- **`templates/patients/patient_list.html`:** Unfold-style header + card, **Bootstrap 5** table, **DataTables 1.13.8** + **Bootstrap 5** styling (CDN)
- **Scripts:** jQuery → Bootstrap bundle → DataTables core → `dataTables.bootstrap5`
- **Defaults:** 25 rows per page, length menu 10/25/50/100, initial sort **Created** descending

### Base layout
- **`{% block extrahead %}`** / **`{% block app_extrahead %}`** — extra CSS in `<head>`
- **`{% block app_scripts %}`** — scripts at the bottom of the page (after the footer, still inside `#page`)

### URL order
- **`patients/api/datatable/`** is registered **before** **`patients/<int:pk>/...`** so `datatable` is not captured as a pk.

Reload `/patients/` after deploy; the grid loads data via AJAX from the new endpoint.