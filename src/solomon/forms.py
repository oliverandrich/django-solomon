from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from solomon.conf import settings

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(
        label=_("E-mail address"),
        widget=forms.EmailInput(attrs={"autofocus": "autofocus"}),
        required=True,
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as e:
            if settings.SOLOMON_SIGNUP_REQUIRED:
                raise forms.ValidationError(
                    _("We could not find a user with that email address.")
                ) from e
        else:
            if not getattr(user, "is_active", True):
                raise forms.ValidationError(_("This user has been deactivated."))

        return email


class SignupForm(forms.Form):
    email = forms.EmailField(
        label=_("E-mail address"),
        widget=forms.EmailInput(attrs={"autofocus": "autofocus"}),
        required=True,
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email address is already linked to an account."))
        return email


class SignupFormWithName(SignupForm):
    name = forms.CharField(
        label=_("Name"),
        widget=forms.TextInput(attrs={"autofocus": "autofocus"}),
        required=True,
    )
    field_order = ["name", "email"]
