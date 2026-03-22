from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import OuterRef, Q, Subquery
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView, UpdateView

from apps.appointments.models import Appointment
from apps.core.mixins import UnfoldAdminContextMixin

from .forms import PatientForm
from .models import Patient

MAX_DATATABLE_PAGE_LENGTH = 100

# DataTables column index -> ORM field for ordering (actions column not sortable)
DATATABLE_ORDER_FIELDS = {
    0: "name",
    1: "phone",
    2: "email",
    3: "date_of_birth",
    4: "next_appointment_at",
    5: "created_at",
}


class ProviderPatientQuerysetMixin:
    """Limit patient objects to the current provider."""

    def get_queryset(self):
        return Patient.objects.filter(provider=self.request.user)


class PatientListView(LoginRequiredMixin, UnfoldAdminContextMixin, TemplateView):
    template_name = "patients/patient_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["datatable_url"] = reverse("patients:datatable")
        return context


class PatientScheduleSearchFragmentView(LoginRequiredMixin, View):
    """HTMX fragment: matching patients for the schedule-appointment modal."""

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        name = (request.GET.get("name") or "").strip()
        phone = (request.GET.get("phone") or "").strip()
        email = (request.GET.get("email") or "").strip()
        q = Q()
        if name:
            q |= Q(name__icontains=name)
        if phone:
            q |= Q(phone__icontains=phone)
        if email:
            q |= Q(email__icontains=email)
        patients = []
        has_any_input = bool(name or phone or email)
        if has_any_input and q:
            patients = list(
                Patient.objects.filter(provider=request.user)
                .filter(q)
                .order_by("name")[:20]
            )
        response = render(
            request,
            "patients/partials/schedule_search_results.html",
            {
                "patients": patients,
                "has_any_input": has_any_input,
            },
        )
        if request.headers.get("HX-Request"):
            response["Cache-Control"] = "no-store"
        return response


class PatientDataTableAjaxView(LoginRequiredMixin, View):
    """DataTables server-side JSON (pagination, ordering, global search)."""

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

        search_value = (request.GET.get("search[value]") or "").strip()

        user = request.user
        now = timezone.now()
        next_sq = (
            Appointment.objects.filter(
                patient_id=OuterRef("pk"),
                scheduled_at__gte=now,
            )
            .order_by("scheduled_at")
            .values("scheduled_at")[:1]
        )
        qs = Patient.objects.filter(provider=user).annotate(
            next_appointment_at=Subquery(next_sq),
        )
        records_total = qs.count()

        if search_value:
            qs = qs.filter(
                Q(name__icontains=search_value)
                | Q(phone__icontains=search_value)
                | Q(email__icontains=search_value)
            )
        records_filtered = qs.count()

        order_col_raw = request.GET.get("order[0][column]")
        order_dir = (request.GET.get("order[0][dir]") or "asc").lower()
        if order_dir not in ("asc", "desc"):
            order_dir = "asc"
        try:
            order_idx = int(order_col_raw) if order_col_raw is not None else 5
        except ValueError:
            order_idx = 5
        order_field = DATATABLE_ORDER_FIELDS.get(order_idx, "created_at")
        # Age column sorts by DOB: ascending age = youngest first = newest DOB first.
        if order_field == "date_of_birth":
            if order_dir == "asc":
                qs = qs.order_by("-date_of_birth", "-pk")
            else:
                qs = qs.order_by("date_of_birth", "-pk")
        else:
            prefix = "-" if order_dir == "desc" else ""
            qs = qs.order_by(f"{prefix}{order_field}", f"{prefix}pk")

        rows = qs[start : start + length]
        data = [self._serialize_patient(p) for p in rows]

        return JsonResponse(
            {
                "draw": draw,
                "recordsTotal": records_total,
                "recordsFiltered": records_filtered,
                "data": data,
            }
        )

    def _serialize_patient(self, p: Patient) -> dict:
        age = p.age_years
        age_display = f"{age} {_('yrs')}" if age is not None else "—"
        na = p.next_appointment_at
        if na:
            local_na = timezone.localtime(na)
            next_display = local_na.strftime("%b %d, %Y %H:%M")
        else:
            next_display = "—"
        local_created = timezone.localtime(p.created_at)
        created_display = local_created.strftime("%b %d, %Y")
        return {
            "pk": p.pk,
            "name": p.name,
            "phone": p.phone or "—",
            "email": p.email or "—",
            "age_display": age_display,
            "next_appointment_display": next_display,
            "created_at_display": created_display,
            "detail_url": reverse("patients:detail", args=[p.pk]),
            "edit_url": reverse("patients:update", args=[p.pk]),
            "delete_url": reverse("patients:delete", args=[p.pk]),
        }


class PatientDetailView(
    LoginRequiredMixin,
    UnfoldAdminContextMixin,
    ProviderPatientQuerysetMixin,
    DetailView,
):
    model = Patient
    template_name = "patients/patient_detail.html"
    context_object_name = "patient"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["appointments"] = self.object.appointments.order_by("-scheduled_at")[:25]
        return context


class PatientCreateView(
    LoginRequiredMixin,
    UnfoldAdminContextMixin,
    CreateView,
):
    model = Patient
    form_class = PatientForm
    template_name = "patients/patient_form.html"

    def get_initial(self):
        initial = super().get_initial()
        if self.request.method == "GET":
            for field in ("name", "phone", "email"):
                val = (self.request.GET.get(field) or "").strip()
                if val:
                    initial[field] = val
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Add patient")
        context["submit_label"] = _("Save patient")
        context["show_save_and_schedule"] = True
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid() and not request.POST.get("confirm_duplicate"):
            phone = (form.cleaned_data.get("phone") or "").strip()
            if phone:
                dupes = Patient.objects.filter(provider=request.user, phone=phone)
                if dupes.exists():
                    context = self.get_context_data(
                        form=form,
                        duplicate_patients=dupes,
                        show_duplicate_warning=True,
                        save_and_schedule_intent=bool(
                            request.POST.get("save_and_schedule")
                        ),
                    )
                    return self.render_to_response(context)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.provider = self.request.user
        if self.request.POST.get("save_and_schedule"):
            messages.success(self.request, _("Patient saved. Continue scheduling below."))
        else:
            messages.success(self.request, _("Patient created."))
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.POST.get("save_and_schedule"):
            return f"{reverse('appointments:create')}?patient={self.object.pk}"
        return reverse("patients:list")


class PatientUpdateView(
    LoginRequiredMixin,
    UnfoldAdminContextMixin,
    ProviderPatientQuerysetMixin,
    UpdateView,
):
    model = Patient
    form_class = PatientForm
    template_name = "patients/patient_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Edit patient")
        context["submit_label"] = _("Update patient")
        context["show_save_and_schedule"] = False
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid() and not request.POST.get("confirm_duplicate"):
            phone = (form.cleaned_data.get("phone") or "").strip()
            if phone:
                dupes = Patient.objects.filter(
                    provider=request.user, phone=phone
                ).exclude(pk=self.object.pk)
                if dupes.exists():
                    context = self.get_context_data(
                        form=form,
                        duplicate_patients=dupes,
                        show_duplicate_warning=True,
                    )
                    return self.render_to_response(context)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, _("Patient updated."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("patients:list")


class PatientDeleteView(
    LoginRequiredMixin,
    UnfoldAdminContextMixin,
    ProviderPatientQuerysetMixin,
    DeleteView,
):
    model = Patient
    template_name = "patients/patient_confirm_delete.html"
    success_url = reverse_lazy("patients:list")

    def delete(self, request, *args, **kwargs):
        messages.success(
            request,
            _("Patient and their appointments have been removed from your active records."),
        )
        return super().delete(request, *args, **kwargs)
