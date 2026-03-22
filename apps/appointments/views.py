from datetime import datetime, time

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from apps.core.mixins import UnfoldAdminContextMixin
from apps.patients.models import Patient

from .forms import AppointmentForm
from .models import Appointment

MAX_DATATABLE_PAGE_LENGTH = 100

DATATABLE_ORDER_FIELDS = {
    0: "patient__name",
    1: "patient__phone",
    2: "patient__email",
    3: "scheduled_at",
    4: "status",
}


def _parse_date_param(value: str):
    if not value or not str(value).strip():
        return None
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _start_of_local_day(d) -> datetime:
    return timezone.make_aware(datetime.combine(d, time.min))


def _end_of_local_day(d) -> datetime:
    return timezone.make_aware(datetime.combine(d, time(23, 59, 59, 999999)))


class ProviderAppointmentQuerysetMixin:
    def get_queryset(self):
        return Appointment.objects.filter(provider=self.request.user).select_related(
            "patient"
        )


class AppointmentListView(LoginRequiredMixin, UnfoldAdminContextMixin, TemplateView):
    template_name = "appointments/appointment_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["datatable_url"] = reverse("appointments:datatable")
        return context


class AppointmentDataTableAjaxView(LoginRequiredMixin, View):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        draw = int(request.GET.get("draw", 1))
        try:
            start = max(0, int(request.GET.get("start", 0)))
            length = int(request.GET.get("length", 25))
        except ValueError:
            start, length = 0, 25
        if length <= 0:
            length = 25
        length = min(length, MAX_DATATABLE_PAGE_LENGTH)

        filter_name = (request.GET.get("filter_patient_name") or "").strip()
        filter_phone = (request.GET.get("filter_patient_phone") or "").strip()
        filter_email = (request.GET.get("filter_patient_email") or "").strip()
        sch_from = _parse_date_param(request.GET.get("filter_scheduled_from") or "")
        sch_to = _parse_date_param(request.GET.get("filter_scheduled_to") or "")
        cr_from = _parse_date_param(request.GET.get("filter_created_from") or "")
        cr_to = _parse_date_param(request.GET.get("filter_created_to") or "")

        qs = Appointment.objects.filter(provider=request.user).select_related("patient")
        records_total = qs.count()

        if filter_name:
            qs = qs.filter(patient__name__icontains=filter_name)
        if filter_phone:
            qs = qs.filter(patient__phone__icontains=filter_phone)
        if filter_email:
            qs = qs.filter(patient__email__icontains=filter_email)
        if sch_from:
            qs = qs.filter(scheduled_at__gte=_start_of_local_day(sch_from))
        if sch_to:
            qs = qs.filter(scheduled_at__lte=_end_of_local_day(sch_to))
        if cr_from:
            qs = qs.filter(created_at__date__gte=cr_from)
        if cr_to:
            qs = qs.filter(created_at__date__lte=cr_to)

        records_filtered = qs.count()

        order_col_raw = request.GET.get("order[0][column]")
        order_dir = (request.GET.get("order[0][dir]") or "desc").lower()
        if order_dir not in ("asc", "desc"):
            order_dir = "desc"
        try:
            order_idx = int(order_col_raw) if order_col_raw is not None else 3
        except ValueError:
            order_idx = 3
        order_field = DATATABLE_ORDER_FIELDS.get(order_idx, "scheduled_at")
        prefix = "-" if order_dir == "desc" else ""
        qs = qs.order_by(f"{prefix}{order_field}", f"{prefix}pk")

        rows = qs[start : start + length]
        data = [self._serialize_row(a) for a in rows]

        return JsonResponse(
            {
                "draw": draw,
                "recordsTotal": records_total,
                "recordsFiltered": records_filtered,
                "data": data,
            }
        )

    def _serialize_row(self, a: Appointment) -> dict:
        p = a.patient
        local_s = timezone.localtime(a.scheduled_at)
        scheduled_display = local_s.strftime("%b %d, %Y %H:%M")
        local_c = timezone.localtime(a.created_at)
        created_display = local_c.strftime("%b %d, %Y %H:%M")
        return {
            "pk": a.pk,
            "patient_name": p.name,
            "patient_phone": p.phone or "—",
            "patient_email": p.email or "—",
            "scheduled_at_display": scheduled_display,
            "status_display": str(a.get_status_display()),
            "status": a.status,
            "created_at_display": created_display,
            "edit_url": reverse("appointments:update", args=[a.pk]),
            "delete_url": reverse("appointments:delete", args=[a.pk]),
        }


class AppointmentCreateView(
    LoginRequiredMixin,
    UnfoldAdminContextMixin,
    CreateView,
):
    model = Appointment
    form_class = AppointmentForm
    template_name = "appointments/appointment_form.html"

    def get_initial(self):
        initial = super().get_initial()
        raw = (self.request.GET.get("patient") or "").strip()
        if raw.isdigit():
            pk = int(raw)
            if Patient.objects.filter(pk=pk, provider_id=self.request.user.pk).exists():
                initial["patient"] = pk
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Schedule appointment")
        context["submit_label"] = _("Save appointment")
        return context

    def form_valid(self, form):
        form.instance.provider = self.request.user
        messages.success(self.request, _("Appointment created."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("appointments:list")


class AppointmentUpdateView(
    LoginRequiredMixin,
    UnfoldAdminContextMixin,
    ProviderAppointmentQuerysetMixin,
    UpdateView,
):
    model = Appointment
    form_class = AppointmentForm
    template_name = "appointments/appointment_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Edit appointment")
        context["submit_label"] = _("Update appointment")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Appointment updated."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("appointments:list")


class AppointmentDeleteView(
    LoginRequiredMixin,
    UnfoldAdminContextMixin,
    ProviderAppointmentQuerysetMixin,
    DeleteView,
):
    model = Appointment
    template_name = "appointments/appointment_confirm_delete.html"
    success_url = reverse_lazy("appointments:list")

    def delete(self, request, *args, **kwargs):
        messages.success(
            request,
            _("Appointment removed from your active records."),
        )
        return super().delete(request, *args, **kwargs)
