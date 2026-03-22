from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class ProviderLoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="provider_test",
            password="correct-pass-123",
        )
        self.login_url = reverse("accounts:login")

    def test_provider_can_log_in_with_correct_credentials(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "provider_test",
                "password": "correct-pass-123",
            },
            follow=False,
        )
        self.assertRedirects(
            response,
            reverse("accounts:dashboard"),
            fetch_redirect_response=False,
        )
        self.assertIn("_auth_user_id", self.client.session)

        dashboard = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertTrue(dashboard.context["user"].is_authenticated)
        self.assertEqual(dashboard.context["user"].pk, self.user.pk)

    def test_login_fails_with_wrong_password(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "provider_test",
                "password": "wrong-password",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertFormError(
            response.context["form"],
            None,
            ["Please enter a correct username and password. Note that both fields may be case-sensitive."],
        )
