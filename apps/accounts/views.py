from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.appointments.models import Appointment
from apps.core.mixins import UnfoldAdminContextMixin
from apps.patients.models import Patient

from .forms import ProviderLoginForm


class ProviderLoginView(UnfoldAdminContextMixin, LoginView):
    template_name = "accounts/login.html"
    authentication_form = ProviderLoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("subtitle", _("Sign in to"))
        context.setdefault("login_heading", _("Provider portal"))
        return context


class ProviderLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class ProviderDashboardView(LoginRequiredMixin, UnfoldAdminContextMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        local_today = timezone.localdate()

        display_name = (user.get_full_name() or "").strip() or user.get_username()
        context["provider_display_name"] = display_name

        patient_count = Patient.objects.filter(provider=user).count()
        context["patient_count"] = patient_count

        today_base = Appointment.objects.filter(
            provider=user, scheduled_at__date=local_today
        ).select_related("patient")
        context["today_appointment_count"] = today_base.count()
        context["today_appointments"] = today_base.order_by("scheduled_at")[:10]

        now = timezone.now()
        context["upcoming_appointments"] = (
            Appointment.objects.filter(
                provider=user,
                scheduled_at__gt=now,
                scheduled_at__date__gt=local_today,
            )
            .select_related("patient")
            .order_by("scheduled_at")[:10]
        )

        return context
