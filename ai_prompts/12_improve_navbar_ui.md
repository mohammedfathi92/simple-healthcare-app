## Prompt

Improve the navbar UI in base.html

Requirements:
- Use Bootstrap navbar
- Add links:
  - Dashboard
  - Patients
  - Appointments
- Highlight the active page
- On the right side, show the logged-in provider name
- Add a Logout button on the right side
- Make the navbar clean and responsive
- The navbar should appear on all pages (use base.html)

Keep the design simple and professional.

## Response


Here is what was finished on top of the navbar work already in place:

### Follow-ups applied

1. **Safe `resolver_match` usage** — Active nav classes only read `namespace` / `url_name` when `request.resolver_match` is set, so 404s or other views without a resolver do not error.

2. **Single Bootstrap load** — Duplicate Bootstrap CSS/JS was removed from `templates/accounts/dashboard.html` and `templates/appointments/appointment_list.html`. They now rely on `base.html` only (modals and toggles still work).

3. **Navbar layout polish** — Replaced non-standard `border-lg-0` utilities with a `.portal-navbar-user-row` class and rules in `custom.css` so the user/logout block gets a top separator on small screens and lines up cleanly on `lg+`.

### Where things live

- **Navbar + Bootstrap links/scripts:** `templates/base.html`
- **Navbar styling:** `static/css/custom.css` (`.portal-bs-navbar`, `.portal-navbar-inner`, `.portal-navbar-user-row`, etc.)

Login still uses Unfold’s unauthenticated layout, so it does not show this bar; every page that extends `base.html` gets the same responsive Bootstrap navbar with Dashboard / Patients / Appointments, active state, provider name, and log out.