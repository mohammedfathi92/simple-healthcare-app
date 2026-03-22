"""Custom view decorators."""

from collections.abc import Callable

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse


def staff_required(
    view_func: Callable[..., HttpResponse],
) -> Callable[..., HttpResponse]:
    """Limit a view to authenticated staff users (``user.is_staff``)."""
    return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)
