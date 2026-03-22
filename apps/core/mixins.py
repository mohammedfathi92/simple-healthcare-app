"""Reusable class-based view mixins."""

from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class UnfoldAdminContextMixin:
    """Merge ``admin.site`` context so Unfold layouts, styles, and theme work outside the admin."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))
        return context


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require an authenticated user with ``is_staff`` (e.g. internal admin views)."""

    def test_func(self) -> bool:
        user = self.request.user
        return user.is_authenticated and user.is_staff
