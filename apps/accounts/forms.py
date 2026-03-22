from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from unfold.widgets import BASE_INPUT_CLASSES

_UNFOLD_INPUT_CLASS = " ".join(BASE_INPUT_CLASSES)


class ProviderLoginForm(AuthenticationForm):
    """Username/password login for providers (uses Django’s built-in authentication)."""

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": _UNFOLD_INPUT_CLASS,
                "autocomplete": "username",
                "autofocus": True,
            }
        )
        self.fields["username"].label = _("Username")
        self.fields["password"].widget.attrs.update(
            {
                "class": _UNFOLD_INPUT_CLASS,
                "autocomplete": "current-password",
            }
        )
        self.fields["password"].label = _("Password")
