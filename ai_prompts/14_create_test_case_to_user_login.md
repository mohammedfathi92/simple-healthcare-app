## Prompt

create a Django TestCase to test user login

Requirements:
- Test that a provider can log in with correct username and password
- Test that login fails with wrong password
- Use reverse() for login URL
- Use setUp() to create a test user
- Place the test in apps/accounts/tests/test_auth.py

***

## Response


Here’s what was added.

### `apps/accounts/tests/__init__.py`
Empty package file so Django discovers tests under `apps.accounts.tests`.

### `apps/accounts/tests/test_auth.py`
- **`setUp()`** – Creates a `CustomUser` with username `provider_test` and password `correct-pass-123`, and sets `self.login_url` via `reverse("accounts:login")`.
- **`test_provider_can_log_in_with_correct_credentials`** – `POST`s to the login URL, expects a redirect to `reverse("accounts:dashboard")`, checks `_auth_user_id` in the session, then loads the dashboard and asserts the user is authenticated and matches `self.user`.
- **`test_login_fails_with_wrong_password`** – `POST`s a bad password, expects 200, no session auth, anonymous user in context, and the usual `AuthenticationForm` non-field error.

Run them with:

`python manage.py test apps.accounts.tests.test_auth`