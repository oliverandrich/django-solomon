from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from solomon.models import SolomonToken

User = get_user_model()


class LoginForm(forms.ModelForm):
    class Meta:
        model = SolomonToken
        fields = ["email", "redirect_url", "ip_address"]
        widgets = {
            "email": forms.EmailInput(attrs={"autofocus": "autofocus"}),
            "redirect_url": forms.HiddenInput(),
            "ip_address": forms.HiddenInput(),
        }

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
