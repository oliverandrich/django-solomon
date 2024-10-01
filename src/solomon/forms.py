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
    redirect_url = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        empty_value=settings.LOGIN_REDIRECT_URL,
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        else:
            if not getattr(user, "is_active", True):
                raise forms.ValidationError(_("This user has been deactivated."))

        return email
