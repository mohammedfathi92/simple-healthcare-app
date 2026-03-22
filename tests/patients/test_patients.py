from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.patients.models import Patient

User = get_user_model()


class PatientCreateTests(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user(
            username="provider_patients",
            password="test-pass-456",
        )
        self.client.login(username="provider_patients", password="test-pass-456")
        self.add_url = reverse("patients:create")

    def test_logged_in_provider_can_create_patient(self):
        self.assertEqual(Patient.objects.filter(provider=self.provider).count(), 0)

        response = self.client.post(
            self.add_url,
            {
                "name": "Jane Doe",
                "phone": "",
                "email": "jane.doe.patient@example.com",
                "date_of_birth": "1990-05-15",
                "medical_history": "",
                "notes": "",
            },
            follow=False,
        )
        self.assertRedirects(
            response,
            reverse("patients:list"),
            fetch_redirect_response=False,
        )

        self.assertEqual(Patient.objects.filter(provider=self.provider).count(), 1)
        patient = Patient.objects.get(email="jane.doe.patient@example.com")
        self.assertEqual(patient.provider_id, self.provider.pk)
        self.assertEqual(patient.name, "Jane Doe")
