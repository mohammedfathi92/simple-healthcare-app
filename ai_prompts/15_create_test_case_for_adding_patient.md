## Prompt
Do the same by creating test for adding a patient.

Requirements:
- Logged-in provider can create a patient
- Check that the patient is linked to the logged-in provider
- Check that the patient is saved in the database
- Use setUp() to create a provider and log in the client
- Use reverse() for patient add URL
- Place the test in tests/patients/test_patients.py

***

## Response


Here’s what was added.

### `tests/patients/__init__.py`
Marks `tests.patients` as a package.

### `tests/patients/test_patients.py`
- **`setUp()`** – Creates user `provider_patients`, logs in with `self.client.login()`, sets `self.add_url` to `reverse("patients:create")`.
- **`test_logged_in_provider_can_create_patient`** – Asserts there are no patients for that provider, `POST`s valid `PatientForm` data (name + email only so the duplicate-phone branch isn’t hit), expects redirect to `reverse("patients:list")`, then checks:
  - exactly one patient for that provider in the DB,
  - `patient.provider_id == self.provider.pk`,
  - saved name/email match.

Run it with:

`python manage.py test tests.patients.test_patients`