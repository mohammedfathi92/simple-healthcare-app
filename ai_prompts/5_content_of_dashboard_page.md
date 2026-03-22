## Prompt

Show in the dashboard:
- welcome message with the provider name
- total number of patients for this provider
- number of today's appointments
- list of today's appointments (time, patient name, status) limit to 10
- list of upcoming appointments  limit to 10 and Ordered by scheduled_at ascending
- two quick action buttons:
  - Add Patient
  - Schedule Appointment

***
## Response


Here’s what was implemented.

### `ProviderDashboardView` (`apps/accounts/views.py`)
- **`provider_display_name`** — full name if set, otherwise username.
- **`patient_count`** — `Patient` rows for `request.user`.
- **`today_appointment_count`** — appointments whose **local calendar date** is today.
- **`today_appointments`** — same filter, `select_related("patient")`, `order_by("scheduled_at")`, **[:10]**.
- **`upcoming_appointments`** — `scheduled_at > now()`, **`scheduled_at__date > local_today`** (so nothing also listed as “later today”), `order_by("scheduled_at")`, **[:10]**, with `select_related("patient")`.

That keeps “today” and “upcoming” from duplicating the same visit.

### `templates/accounts/dashboard.html`
- Welcome line: **“Welcome, {{ provider_display_name }}”**.
- Stat cards: **Patients** and **Today’s appointments** (count).
- **Today’s appointments** table: **time** (`localtime` + `SHORT`), **patient**, **status** (via `get_status_display`), max 10.
- **Upcoming** table: **date**, **time**, **patient**, **status**, max 10.
- Quick actions: **Add Patient** → `admin:patients_patient_add`, **Schedule Appointment** → `admin:appointments_appointment_add`.
- **Open admin** kept at the bottom.

Styling follows your existing Unfold-style utility classes. If you want “upcoming” to include **later today** as well (and allow overlap with the today table), say so and we can switch the filter.