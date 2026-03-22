## Prompt

create a login system for providers using Django authentication with the following requirements:
- Login page at /login
- Logout at /logout
- Dashboard at /dashboard
- Use bootstrap 5 for a clean UI
- Create base.html and extend from it
- Only logged-in users can access the dashboard
- Use class-based views
- Use Django forms
- Show error message if login fails

and to do that create this files:

- apps/accounts/views.py
- apps/accounts/forms.py
- apps/accounts/urls.py
- templates/accounts/login.html
- templates/accounts/dashboard.html
- templates/base.html

***

## Response


Here’s what was added and how it behaves.

### Files

| File | Role |
|------|------|
| `apps/accounts/forms.py` | `ProviderLoginForm` subclasses `AuthenticationForm` and adds Bootstrap `form-control` + labels. |
| `apps/accounts/views.py` | `ProviderLoginView` (`LoginView`), `ProviderLogoutView` (`LogoutView`), `ProviderDashboardView` (`LoginRequiredMixin` + `TemplateView`). |
| `apps/accounts/urls.py` | `/login/`, `/logout/`, `/dashboard/` with `app_name = "accounts"`. |
| `templates/base.html` | Bootstrap 5 (CDN), navbar, messages (maps Django’s `error` → `alert-danger`), `{% block content %}`. |
| `templates/accounts/login.html` | Card layout, CSRF, `non_field_errors` + field errors for failed login. |
| `templates/accounts/dashboard.html` | Welcome copy + link to `/admin/`. |

### Project wiring

- `config/urls.py` — `path("", include("apps.accounts.urls"))`.
- `config/settings.py` — `TEMPLATES["DIRS"] = [BASE_DIR / "templates"]`, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`.

### Behaviour

- **Dashboard** is protected with `LoginRequiredMixin` (uses `LOGIN_URL` → `/login/`).
- **Login** uses your **`ProviderLoginForm`**; bad credentials show **`invalid_login`** (and related) as **`non_field_errors`** in a red alert.
- **Logout** in Django 6’s `LogoutView` is **POST-only**. The navbar **“Log out”** button submits a POST to `/logout/` with CSRF (correct pattern).

URL names: `accounts:login`, `accounts:logout`, `accounts:dashboard`. After a successful login, users go to **`/dashboard/`** per `LOGIN_REDIRECT_URL`.