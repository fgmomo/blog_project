from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class SignUpForm(UserCreationForm):

    email = forms.EmailField()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

        self.fields["username"].help_text = None
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec cet email.")

        return email


class ProfileEditForm(forms.ModelForm):

    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ["profile_picture"]

    def __init__(self, *args, user=None, **kwargs):
        self.user = user

        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields["email"].initial = user.email

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Un compte existe déjà avec cet email.")

        return email

    def save(self, commit=True):
        profile = super().save(commit=commit)

        if self.user is not None:
            self.user.email = self.cleaned_data["email"]

            if commit:
                self.user.save(update_fields=["email"])

        return profile