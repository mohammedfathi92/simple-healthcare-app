## Prompt

Install django-unfold and configure it as the admin theme
make sure it works well with Django and HTMX, keep the UI clean and modern

***

## Response


Here’s what was set up.

### Package
- **`django-unfold==0.86.1`** added to `requirements.txt` and installed in the venv.

### `config/settings.py`
- **`unfold`**, **`unfold.contrib.filters`**, and **`unfold.contrib.forms`** are registered **before** **`django.contrib.admin`** (required for Unfold).
- **`django_htmx`** is in `INSTALLED_APPS` and **`django_htmx.middleware.HtmxMiddleware`** is at the end of `MIDDLEWARE` so your own views can use **`request.htmx`** and HTMX headers without touching the admin.
- **`UNFOLD`** configures branding (healthcare-oriented title/header, **`local_hospital`** symbol), **8px** corners, sidebar search + “all applications”, a short **Workspace** nav (Dashboard, Providers, Patients, Appointments), and an **environment** badge (Development / Production).

### Admin classes
- **`PatientAdmin`** and **`AppointmentAdmin`** subclass **`unfold.admin.ModelAdmin`**.
- **`UserAdmin`** subclasses **`DjangoUserAdmin`** and **`ModelAdmin`**, and uses Unfold’s **`UserChangeForm`**, **`UserCreationForm`**, and **`AdminPasswordChangeForm`** so user screens match the theme.

### Django + HTMX + Unfold
- The **admin** is fully styled by **Unfold** (it uses its own layout and **Alpine.js** there).
- **HTMX** applies to **your** URLs/templates via **django-htmx**; it does not load inside the admin by default, so there’s no script clash. For HTMX partials, use normal templates and `request.htmx` as needed; keep using **`{% load static %}`** and the **`htmx.org`** script on those pages only.

Restart **`runserver`** and open **`/admin/`** to see the new UI. If anything 404s on first load, run **`python manage.py collectstatic`** when `DEBUG=False` behind a real static server.